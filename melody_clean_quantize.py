import sys
import os
import json
import math

from mido import MidiFile, MidiTrack, Message, MetaMessage


# ============================================================
# 基本參數
# ============================================================

# 最短音符時間（秒）
MIN_NOTE_LENGTH_SEC = 0.060

# 1/16 拍
QUANTIZE_GRID = 0.25

# 人聲合理音域：C3 ~ C6
MIN_MIDI_NOTE = 48
MAX_MIDI_NOTE = 84

# 最低 velocity
VELOCITY_THRESHOLD = 12

# 旋律最大合理跳躍
MAX_MELODY_JUMP = 12

# 太大的跳躍視為可疑
LARGE_JUMP = 7

# 太短的音符
VERY_SHORT_RATIO = 0.12

# 旋律候選搜尋範圍
LOOK_AHEAD_TICKS = 240


# ============================================================
# info.json
# ============================================================

def load_info(info_json):
    info = {
        "tempo_scale": 1.0,
        "real_bpm": 120.0,
        "key_tonic": "C",
        "key_mode": "major",
    }

    if not info_json or not os.path.isfile(info_json):
        print("⚠ 找不到 info.json，使用預設 BPM=120")
        return info

    try:
        with open(info_json, "r", encoding="utf-8") as f:
            data = json.load(f)

        info.update(data)

    except Exception as exc:
        print(f"⚠ info.json 讀取失敗：{exc}")

    try:
        info["tempo_scale"] = float(info.get("tempo_scale", 1.0))
    except Exception:
        info["tempo_scale"] = 1.0

    try:
        info["real_bpm"] = float(info.get("real_bpm", 120.0))
    except Exception:
        info["real_bpm"] = 120.0

    if not 0.25 <= info["tempo_scale"] <= 2.5:
        info["tempo_scale"] = 1.0

    print(
        f"✓ BPM 校正比例={info['tempo_scale']:.4f}, "
        f"real_bpm={info['real_bpm']:.2f}"
    )

    if info.get("key_tonic"):
        print(
            f"✓ 調性={info.get('key_tonic')} "
            f"{info.get('key_mode', 'major')}"
        )

    return info


# ============================================================
# MIDI 讀取
# ============================================================

def read_midi(filename):
    mid = MidiFile(filename)

    ticks_per_beat = mid.ticks_per_beat

    events = []

    for track_index, track in enumerate(mid.tracks):

        current_tick = 0

        active = {}

        for msg in track:

            current_tick += msg.time

            # Note ON
            if msg.type == "note_on" and msg.velocity > 0:

                key = msg.note

                # BasicPitch 偶爾會出現同音重複 note_on
                # 如果已存在，先結束舊音符
                if key in active:

                    old_start, old_velocity = active[key]

                    duration = current_tick - old_start

                    if duration > 0:

                        events.append({
                            "start": old_start,
                            "duration": duration,
                            "note": key,
                            "velocity": old_velocity,
                            "track": track_index,
                        })

                active[key] = (
                    current_tick,
                    msg.velocity
                )

            # Note OFF
            elif (
                msg.type == "note_off"
                or (
                    msg.type == "note_on"
                    and msg.velocity == 0
                )
            ):

                key = msg.note

                if key in active:

                    start_tick, velocity = active.pop(key)

                    duration = current_tick - start_tick

                    if duration > 0:

                        events.append({
                            "start": start_tick,
                            "duration": duration,
                            "note": key,
                            "velocity": velocity,
                            "track": track_index,
                        })

    events.sort(
        key=lambda e: (
            e["start"],
            e["note"]
        )
    )

    return events, ticks_per_beat


# ============================================================
# BPM 時間校正
# ============================================================

def apply_tempo_scale(events, tempo_scale):

    if abs(tempo_scale - 1.0) < 0.0001:
        return events

    print(
        f"✓ 套用 tempo_scale={tempo_scale:.4f}"
    )

    for e in events:

        e["start"] = int(
            round(e["start"] * tempo_scale)
        )

        e["duration"] = max(
            1,
            int(
                round(
                    e["duration"] * tempo_scale
                )
            )
        )

    return events


# ============================================================
# 音域
# ============================================================

def filter_pitch_range(events):

    result = []

    for e in events:

        note = int(e["note"])

        if MIN_MIDI_NOTE <= note <= MAX_MIDI_NOTE:

            result.append(e)

    return result


# ============================================================
# 修正極端音高
# ============================================================

def fix_pitch(note):

    note = int(note)

    while note < MIN_MIDI_NOTE:
        note += 12

    while note > MAX_MIDI_NOTE:
        note -= 12

    return note


# ============================================================
# 短音 / 雜訊
# ============================================================

def remove_noise(events, ticks_per_beat):

    # 例如 480 TPB：
    # 0.06 秒大約 29 ticks
    min_ticks = max(
        20,
        int(
            ticks_per_beat
            * 0.125
        )
    )

    result = []

    for e in events:

        duration = e["duration"]
        velocity = e["velocity"]

        # 正常音符
        if duration >= min_ticks:

            if velocity >= VELOCITY_THRESHOLD:
                result.append(e)

            continue

        # 很短的音符只保留比較強的
        if (
            duration >= min_ticks * 0.5
            and velocity >= 35
        ):
            result.append(e)

    return result


# ============================================================
# 音符評分
# ============================================================

def note_score(event, previous=None, ticks_per_beat=480):

    score = 0.0

    velocity = float(event["velocity"])

    duration = float(event["duration"])

    note = int(event["note"])

    # --------------------------------------------------------
    # 1. velocity
    # --------------------------------------------------------

    score += min(
        velocity,
        100
    ) * 0.20

    # --------------------------------------------------------
    # 2. 長音通常比較像主旋律
    # --------------------------------------------------------

    quarter_length = (
        duration / ticks_per_beat
    )

    score += min(
        quarter_length,
        2.0
    ) * 8.0

    # --------------------------------------------------------
    # 3. 音域偏好
    # --------------------------------------------------------

    # 人聲中音區給一點優勢
    if 55 <= note <= 78:
        score += 5

    # --------------------------------------------------------
    # 4. 與上一個音符的連續性
    # --------------------------------------------------------

    if previous is not None:

        diff = abs(
            note - int(previous["note"])
        )

        if diff == 0:
            score += 8

        elif diff <= 2:
            score += 10

        elif diff <= 4:
            score += 7

        elif diff <= 7:
            score += 3

        elif diff <= LARGE_JUMP:
            score -= 5

        elif diff <= MAX_MELODY_JUMP:
            score -= 12

        else:
            score -= 30

    return score


# ============================================================
# 找出同時間附近的候選音符
# ============================================================

def build_candidate_groups(events, tolerance):

    events = sorted(
        events,
        key=lambda e: (
            e["start"],
            e["note"]
        )
    )

    groups = []

    current = []

    current_start = None

    for e in events:

        start = e["start"]

        if current_start is None:

            current_start = start
            current = [e]
            continue

        if start - current_start <= tolerance:

            current.append(e)

        else:

            groups.append(current)

            current_start = start

            current = [e]

    if current:
        groups.append(current)

    return groups


# ============================================================
# 旋律追蹤 V2
# ============================================================

def choose_melody_v2(
    events,
    ticks_per_beat
):

    if not events:
        return []

    events = sorted(
        events,
        key=lambda e: (
            e["start"],
            e["note"]
        )
    )

    # --------------------------------------------------------
    # 將非常接近的音符視為同一組候選
    # --------------------------------------------------------

    tolerance = max(
        20,
        int(
            ticks_per_beat * 0.10
        )
    )

    groups = build_candidate_groups(
        events,
        tolerance
    )

    print(
        f"旋律候選群組: {len(groups)}"
    )

    melody = []

    previous = None

    for group in groups:

        if not group:
            continue

        best = None

        best_score = -999999

        for candidate in group:

            score = note_score(
                candidate,
                previous,
                ticks_per_beat
            )

            # ------------------------------------------------
            # 如果和上一個音符重疊
            # 優先考慮較自然的旋律
            # ------------------------------------------------

            if previous is not None:

                prev_end = (
                    previous["start"]
                    + previous["duration"]
                )

                if candidate["start"] < prev_end:

                    diff = abs(
                        candidate["note"]
                        - previous["note"]
                    )

                    if diff <= 4:
                        score += 12

                    elif diff <= 7:
                        score += 2

                    else:
                        score -= 10

            if score > best_score:

                best_score = score
                best = candidate

        if best is None:
            continue

        # ----------------------------------------------------
        # 防止不合理的大跳躍
        # ----------------------------------------------------

        if previous is not None:

            diff = abs(
                best["note"]
                - previous["note"]
            )

            if diff > MAX_MELODY_JUMP:

                alternatives = []

                for candidate in group:

                    alt_diff = abs(
                        candidate["note"]
                        - previous["note"]
                    )

                    if alt_diff <= MAX_MELODY_JUMP:

                        alternatives.append(
                            (
                                alt_diff,
                                candidate
                            )
                        )

                if alternatives:

                    alternatives.sort(
                        key=lambda x: x[0]
                    )

                    best = alternatives[0][1]

        # ----------------------------------------------------
        # 複製 event
        # ----------------------------------------------------

        selected = dict(best)

        melody.append(selected)

        previous = selected

    return melody


# ============================================================
# 合併非常接近的同音
# ============================================================

def merge_same_pitch(events, ticks_per_beat):

    if not events:
        return []

    events = sorted(
        events,
        key=lambda e: (
            e["start"],
            e["note"]
        )
    )

    result = []

    merge_gap = max(
        10,
        int(
            ticks_per_beat * 0.08
        )
    )

    for e in events:

        if not result:

            result.append(
                dict(e)
            )

            continue

        prev = result[-1]

        prev_end = (
            prev["start"]
            + prev["duration"]
        )

        gap = (
            e["start"]
            - prev_end
        )

        if (
            e["note"] == prev["note"]
            and gap <= merge_gap
        ):

            new_end = max(
                prev_end,
                e["start"]
                + e["duration"]
            )

            prev["duration"] = (
                new_end
                - prev["start"]
            )

            prev["velocity"] = max(
                prev["velocity"],
                e["velocity"]
            )

        else:

            result.append(
                dict(e)
            )

    return result


# ============================================================
# 量化
# ============================================================

def quantize_events(
    events,
    ticks_per_beat
):

    grid = (
        ticks_per_beat
        * QUANTIZE_GRID
    )

    result = []

    for e in events:

        start = float(e["start"])

        end = float(
            e["start"]
            + e["duration"]
        )

        qstart = int(
            round(
                start / grid
            )
            * grid
        )

        qend = int(
            round(
                end / grid
            )
            * grid
        )

        if qend <= qstart:

            qend = (
                qstart
                + int(grid)
            )

        new_event = dict(e)

        new_event["start"] = qstart

        new_event["duration"] = (
            qend - qstart
        )

        result.append(
            new_event
        )

    return result


# ============================================================
# 重疊修正
# ============================================================

def fix_overlaps(events):

    if not events:
        return []

    events = sorted(
        events,
        key=lambda e: (
            e["start"],
            e["note"]
        )
    )

    result = []

    for e in events:

        e = dict(e)

        if not result:

            result.append(e)

            continue

        prev = result[-1]

        prev_end = (
            prev["start"]
            + prev["duration"]
        )

        # ----------------------------------------------------
        # 沒有重疊
        # ----------------------------------------------------

        if e["start"] >= prev_end:

            result.append(e)

            continue

        # ----------------------------------------------------
        # 重疊
        # ----------------------------------------------------

        new_duration = (
            e["start"]
            - prev["start"]
        )

        # 如果新音符完全蓋住舊音符
        if new_duration <= 0:

            if (
                e["velocity"]
                > prev["velocity"]
            ):

                result[-1] = e

            continue

        prev["duration"] = (
            new_duration
        )

        if prev["duration"] > 0:

            result.append(e)

    return [
        e
        for e in result
        if e["duration"] > 0
    ]


# ============================================================
# 消除過短音符
# ============================================================

def remove_tiny_after_quantize(
    events,
    ticks_per_beat
):

    minimum = max(
        30,
        int(
            ticks_per_beat
            * 0.125
        )
    )

    result = []

    for e in events:

        if e["duration"] >= minimum:

            result.append(e)

    return result


# ============================================================
# 修正音符位置
# ============================================================

def normalize_events(events):

    result = []

    for e in events:

        item = dict(e)

        item["note"] = fix_pitch(
            item["note"]
        )

        item["start"] = max(
            0,
            int(item["start"])
        )

        item["duration"] = max(
            1,
            int(item["duration"])
        )

        item["velocity"] = max(
            1,
            min(
                127,
                int(item["velocity"])
            )
        )

        result.append(item)

    return result


# ============================================================
# 寫 MIDI
# ============================================================

def write_midi(
    events,
    output_file,
    ticks_per_beat,
    bpm=120
):

    mid = MidiFile(
        ticks_per_beat=ticks_per_beat
    )

    track = MidiTrack()

    mid.tracks.append(track)

    tempo_us = int(
        round(
            60_000_000
            / max(
                20,
                bpm
            )
        )
    )

    track.append(
        MetaMessage(
            "set_tempo",
            tempo=tempo_us,
            time=0
        )
    )

    track.append(
        MetaMessage(
            "time_signature",
            numerator=4,
            denominator=4,
            clocks_per_click=24,
            notated_32nd_notes_per_beat=8,
            time=0
        )
    )

    messages = []

    for e in events:

        start = int(
            e["start"]
        )

        end = int(
            e["start"]
            + e["duration"]
        )

        note = int(
            e["note"]
        )

        velocity = int(
            max(
                1,
                min(
                    127,
                    e["velocity"]
                )
            )
        )

        messages.append(
            (
                start,
                1,
                Message(
                    "note_on",
                    note=note,
                    velocity=velocity,
                    time=0
                )
            )
        )

        messages.append(
            (
                end,
                0,
                Message(
                    "note_off",
                    note=note,
                    velocity=0,
                    time=0
                )
            )
        )

    # note_off 先於 note_on
    # 避免同 tick 音符互相重疊
    messages.sort(
        key=lambda x: (
            x[0],
            x[1]
        )
    )

    previous_tick = 0

    for tick, _, msg in messages:

        msg.time = max(
            0,
            int(
                tick
                - previous_tick
            )
        )

        track.append(msg)

        previous_tick = tick

    track.append(
        MetaMessage(
            "end_of_track",
            time=0
        )
    )

    mid.save(
        output_file
    )


# ============================================================
# 主流程
# ============================================================

def process(
    input_file,
    output_file,
    info_json=None
):

    print(
        "========================================"
    )

    print(
        "[4/6] 精準旋律清理 + 量化 V2"
    )

    print(
        "========================================"
    )

    # --------------------------------------------------------
    # 1. 讀取資訊
    # --------------------------------------------------------

    info = load_info(
        info_json
    )

    tempo_scale = info[
        "tempo_scale"
    ]

    real_bpm = info[
        "real_bpm"
    ]

    # --------------------------------------------------------
    # 2. 讀取 MIDI
    # --------------------------------------------------------

    events, tpb = read_midi(
        input_file
    )

    print(
        f"原始音符: {len(events)}"
    )

    if not events:

        raise RuntimeError(
            "MIDI 沒有找到任何音符"
        )

    # --------------------------------------------------------
    # 3. BPM 校正
    # --------------------------------------------------------

    events = apply_tempo_scale(
        events,
        tempo_scale
    )

    # --------------------------------------------------------
    # 4. 音域篩選
    # --------------------------------------------------------

    events = filter_pitch_range(
        events
    )

    print(
        f"音域篩選: {len(events)}"
    )

    # --------------------------------------------------------
    # 5. 音高標準化
    # --------------------------------------------------------

    for e in events:

        e["note"] = fix_pitch(
            e["note"]
        )

    # --------------------------------------------------------
    # 6. 雜訊清理
    # --------------------------------------------------------

    events = remove_noise(
        events,
        tpb
    )

    print(
        f"雜訊過濾: {len(events)}"
    )

    # --------------------------------------------------------
    # 7. 旋律追蹤 V2
    # --------------------------------------------------------

    melody = choose_melody_v2(
        events,
        tpb
    )

    print(
        f"旋律追蹤 V2: {len(melody)}"
    )

    if not melody:

        raise RuntimeError(
            "旋律追蹤後沒有剩餘音符"
        )

    # --------------------------------------------------------
    # 8. 合併同音
    # --------------------------------------------------------

    melody = merge_same_pitch(
        melody,
        tpb
    )

    print(
        f"同音合併: {len(melody)}"
    )

    # --------------------------------------------------------
    # 9. 量化
    # --------------------------------------------------------

    melody = quantize_events(
        melody,
        tpb
    )

    # --------------------------------------------------------
    # 10. 修正重疊
    # --------------------------------------------------------

    melody = fix_overlaps(
        melody
    )

    # --------------------------------------------------------
    # 11. 移除量化後太短音符
    # --------------------------------------------------------

    melody = remove_tiny_after_quantize(
        melody,
        tpb
    )

    # --------------------------------------------------------
    # 12. 最後標準化
    # --------------------------------------------------------

    melody = normalize_events(
        melody
    )

    melody = sorted(
        melody,
        key=lambda e: (
            e["start"],
            e["note"]
        )
    )

    print(
        f"最終音符: {len(melody)}"
    )

    # --------------------------------------------------------
    # 13. 輸出 MIDI
    # --------------------------------------------------------

    write_midi(
        melody,
        output_file,
        tpb,
        real_bpm
    )

    print(
        f"完成: {output_file}"
    )


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":

    if len(sys.argv) < 3:

        print(
            "使用方法:"
        )

        print(
            "python melody_clean_quantize_v2.py "
            "input.mid output.mid [info.json]"
        )

        sys.exit(1)

    process(
        sys.argv[1],
        sys.argv[2],
        sys.argv[3]
        if len(sys.argv) > 3
        else None
    )

