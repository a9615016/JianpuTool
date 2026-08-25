import sys
import os
import math
from collections import defaultdict

from mido import (
    MidiFile,
    MidiTrack,
    Message,
    MetaMessage
)


# ============================================================
# 基本參數
# ============================================================

# 最短音符時間（秒）
MIN_NOTE_LENGTH_SEC = 0.060

# MIDI 音符合理人聲範圍
# C3 = 48
# C6 = 84
MIN_PITCH = 48
MAX_PITCH = 84

# 1/16 拍
# quarter note = 1
# eighth = 0.5
# sixteenth = 0.25
QUANTIZE_GRID = 0.25

# 是否強制單音旋律
MONOPHONIC = True

# 最大同時音符
# 單旋律 = 1
MAX_POLYPHONY = 1


# ============================================================
# Note 資料結構
# ============================================================

class NoteData:

    def __init__(
        self,
        pitch,
        start,
        end,
        velocity=80,
        channel=0
    ):
        self.pitch = int(pitch)
        self.start = float(start)
        self.end = float(end)
        self.velocity = int(velocity)
        self.channel = int(channel)

    @property
    def duration(self):
        return max(0.0, self.end - self.start)

    def copy(self):
        return NoteData(
            self.pitch,
            self.start,
            self.end,
            self.velocity,
            self.channel
        )

    def __repr__(self):
        return (
            f"Note("
            f"{self.pitch}, "
            f"{self.start:.4f}, "
            f"{self.end:.4f}, "
            f"dur={self.duration:.4f}"
            f")"
        )


# ============================================================
# MIDI 時間工具
# ============================================================

def get_tempo(mid):
    """
    取得第一個 tempo。
    預設 120 BPM。
    """

    for track in mid.tracks:

        for msg in track:

            if (
                msg.is_meta
                and msg.type == "set_tempo"
            ):
                return msg.tempo

    # 120 BPM
    return 500000


def get_time_signature(mid):
    """
    取得第一個 Time Signature。

    預設 4/4。
    """

    for track in mid.tracks:

        for msg in track:

            if (
                msg.is_meta
                and msg.type == "time_signature"
            ):
                return (
                    msg.numerator,
                    msg.denominator
                )

    return 4, 4


def get_ticks_per_beat(mid):

    return mid.ticks_per_beat


# ============================================================
# MIDI → 秒
# ============================================================

def collect_midi_notes(mid):
    """
    讀取所有 MIDI track 的 note。

    回傳：

        notes
        meta_events
    """

    notes = []

    # 每個 track 都要自己的 note stack
    for track_index, track in enumerate(mid.tracks):

        absolute_tick = 0

        active = defaultdict(list)

        for msg in track:

            absolute_tick += msg.time

            if msg.type == "note_on" and msg.velocity > 0:

                active[
                    (msg.channel, msg.note)
                ].append(
                    (
                        absolute_tick,
                        msg.velocity
                    )
                )

            elif (
                msg.type == "note_off"
                or (
                    msg.type == "note_on"
                    and msg.velocity == 0
                )
            ):

                key = (msg.channel, msg.note)

                if active[key]:

                    start_tick, velocity = active[key].pop()

                    if absolute_tick > start_tick:

                        notes.append(
                            {
                                "track": track_index,
                                "channel": msg.channel,
                                "pitch": msg.note,
                                "start_tick": start_tick,
                                "end_tick": absolute_tick,
                                "velocity": velocity
                            }
                        )

    return notes


# ============================================================
# MIDI tick → quarter beat
# ============================================================

def tick_to_beat(tick, ticks_per_beat):

    return tick / float(ticks_per_beat)


# ============================================================
# 取得旋律音符
# ============================================================

def extract_melody(mid):

    raw_notes = collect_midi_notes(mid)

    ticks_per_beat = mid.ticks_per_beat

    notes = []

    for n in raw_notes:

        start = tick_to_beat(
            n["start_tick"],
            ticks_per_beat
        )

        end = tick_to_beat(
            n["end_tick"],
            ticks_per_beat
        )

        notes.append(
            NoteData(
                pitch=n["pitch"],
                start=start,
                end=end,
                velocity=n["velocity"],
                channel=n["channel"]
            )
        )

    return notes


# ============================================================
# 音域過濾
# ============================================================

def filter_pitch_range(notes):

    result = []

    for n in notes:

        if MIN_PITCH <= n.pitch <= MAX_PITCH:

            result.append(n)

    return result


# ============================================================
# 去除太短音符
# ============================================================

def remove_short_notes(notes):

    result = []

    for n in notes:

        if n.duration >= MIN_NOTE_LENGTH_SEC:

            result.append(n)

    return result


# ============================================================
# 量化時間
# ============================================================

def quantize_value(value):

    return round(
        value / QUANTIZE_GRID
    ) * QUANTIZE_GRID


def quantize_notes(notes):

    result = []

    for n in notes:

        start = quantize_value(n.start)
        end = quantize_value(n.end)

        # 避免量化後變成 0 長度
        if end <= start:

            end = (
                start
                + QUANTIZE_GRID
            )

        new_note = NoteData(
            pitch=n.pitch,
            start=start,
            end=end,
            velocity=n.velocity,
            channel=n.channel
        )

        result.append(new_note)

    return result


# ============================================================
# 排序
# ============================================================

def sort_notes(notes):

    return sorted(
        notes,
        key=lambda n: (
            n.start,
            n.end,
            n.pitch
        )
    )


# ============================================================
# 單音旋律處理
# ============================================================

def make_monophonic(notes):

    if not notes:

        return []

    notes = sort_notes(notes)

    result = []

    current_end = -1

    for note in notes:

        # 第一個
        if not result:

            result.append(
                note.copy()
            )

            current_end = note.end

            continue

        previous = result[-1]

        # ----------------------------------------------------
        # 情況 1：
        # 新音符開始 >= 前一個結束
        # ----------------------------------------------------

        if note.start >= previous.end:

            result.append(
                note.copy()
            )

            current_end = note.end

            continue

        # ----------------------------------------------------
        # 情況 2：
        # 音符重疊
        # ----------------------------------------------------

        if note.start < previous.end:

            # 如果同音高
            if note.pitch == previous.pitch:

                # 延長前一個
                previous.end = max(
                    previous.end,
                    note.end
                )

                current_end = previous.end

                continue

            # ------------------------------------------------
            # 不同音高：
            # 保留較長的音符
            # ------------------------------------------------

            previous_duration = (
                previous.end
                - previous.start
            )

            note_duration = (
                note.end
                - note.start
            )

            if note_duration > previous_duration:

                # 移除前一個
                result.pop()

                # 新音符從目前位置開始
                new_note = note.copy()

                # 避免與更前面的音符重疊
                if result:

                    last = result[-1]

                    if new_note.start < last.end:

                        new_note.start = last.end

                if new_note.end > new_note.start:

                    result.append(
                        new_note
                    )

                    current_end = new_note.end

            else:

                # 保留前一個
                continue

    return result


# ============================================================
# ★ 修正音符間重疊
# ============================================================

def fix_overlaps(notes):

    if not notes:

        return []

    notes = sort_notes(notes)

    result = []

    for note in notes:

        note = note.copy()

        if not result:

            result.append(note)

            continue

        previous = result[-1]

        # 如果新音符開始時間早於上一音符結束
        if note.start < previous.end:

            # 同音高：
            # 視為延音
            if note.pitch == previous.pitch:

                previous.end = max(
                    previous.end,
                    note.end
                )

                continue

            # 不同音高：
            # 把前一音符切到新音符開始
            previous.end = note.start

            # 如果前一個因此變成 0
            if previous.end <= previous.start:

                result.pop()

        if note.end > note.start:

            result.append(note)

    return result


# ============================================================
# ★★★ 核心：
# 修正跨小節音符
# ============================================================

def split_notes_at_barlines(
    notes,
    numerator=4,
    denominator=4
):
    """
    將所有跨小節音符切開。

    例如：

        4/4

        小節：
        0 ───────── 4 ───────── 8

        原音符：
        3.5 ───────────── 5

        會變成：

        3.5 ─── 4
        4 ───── 5

    保證：

        note.end <= bar_end

    所以任何單一 MIDI note
    都不會跨越小節線。

    """

    if not notes:

        return []

    # 一拍 = quarter note
    beats_per_measure = (
        numerator
        * (4.0 / denominator)
    )

    if beats_per_measure <= 0:

        beats_per_measure = 4.0

    result = []

    for note in notes:

        start = note.start
        end = note.end

        if end <= start:

            continue

        current_start = start

        # ----------------------------------------------------
        # 不斷切割直到音符結束
        # ----------------------------------------------------

        safety = 0

        while current_start < end:

            safety += 1

            if safety > 10000:

                print(
                    "⚠️ 警告：音符切割超過安全次數"
                )

                break

            # 找到 current_start 所在的小節
            measure_index = math.floor(
                current_start
                / beats_per_measure
            )

            bar_end = (
                measure_index + 1
            ) * beats_per_measure

            # 本段結束點
            segment_end = min(
                end,
                bar_end
            )

            # 防止浮點數造成問題
            if segment_end <= current_start:

                segment_end = (
                    current_start
                    + QUANTIZE_GRID
                )

                segment_end = min(
                    segment_end,
                    end
                )

            # ------------------------------------------------
            # 建立小節內音符
            # ------------------------------------------------

            segment = NoteData(
                pitch=note.pitch,
                start=current_start,
                end=segment_end,
                velocity=note.velocity,
                channel=note.channel
            )

            if segment.duration > 0:

                result.append(segment)

            current_start = segment_end

    return result


# ============================================================
# ★ 修正量化後跨小節問題
# ============================================================

def fix_cross_measure_after_quantize(
    notes,
    numerator=4,
    denominator=4
):
    """
    第二次檢查。

    因為量化可能造成：

        start = 3.75
        end   = 4.25

    所以這裡再做一次 barline split。

    """

    notes = sort_notes(notes)

    notes = split_notes_at_barlines(
        notes,
        numerator,
        denominator
    )

    return notes


# ============================================================
# 移除極短切割音符
# ============================================================

def remove_tiny_segments(notes):

    result = []

    for note in notes:

        # 正常保留
        if note.duration >= 0.01:

            result.append(note)

    return result


# ============================================================
# 合併相鄰同音符
# ============================================================

def merge_adjacent_same_pitch(
    notes,
    numerator=4,
    denominator=4
):
    """
    注意：

    不能把跨小節的音符合併回去。

    因此只有：

        A.end == B.start

    且兩者仍然在同一小節內

    才合併。

    """

    if not notes:

        return []

    notes = sort_notes(notes)

    beats_per_measure = (
        numerator
        * (4.0 / denominator)
    )

    result = []

    for note in notes:

        if not result:

            result.append(
                note.copy()
            )

            continue

        previous = result[-1]

        same_pitch = (
            previous.pitch
            == note.pitch
        )

        adjacent = abs(
            previous.end
            - note.start
        ) < 1e-8

        if same_pitch and adjacent:

            # ------------------------------------------------
            # 判斷是否跨小節
            # ------------------------------------------------

            previous_measure = math.floor(
                previous.start
                / beats_per_measure
            )

            note_measure = math.floor(
                note.start
                / beats_per_measure
            )

            # 同一小節才合併
            if (
                previous_measure
                == note_measure
            ):

                previous.end = note.end

                continue

        result.append(
            note.copy()
        )

    return result


# ============================================================
# 確保每個音符都在小節內
# ============================================================

def validate_bar_boundaries(
    notes,
    numerator=4,
    denominator=4
):
    """
    檢查：

        note.end 不得超過小節尾端
        note.start 不得小於小節開始

    """

    beats_per_measure = (
        numerator
        * (4.0 / denominator)
    )

    errors = []

    for index, note in enumerate(notes):

        measure_index = math.floor(
            note.start
            / beats_per_measure
        )

        measure_start = (
            measure_index
            * beats_per_measure
        )

        measure_end = (
            measure_index + 1
        ) * beats_per_measure

        # start 越界
        if (
            note.start
            < measure_start - 1e-7
        ):

            errors.append(
                (
                    index,
                    "START",
                    note
                )
            )

        # end 越界
        if (
            note.end
            > measure_end + 1e-7
        ):

            errors.append(
                (
                    index,
                    "END",
                    note
                )
            )

    return errors


# ============================================================
# Beat → MIDI Tick
# ============================================================

def beat_to_tick(
    beat,
    ticks_per_beat
):

    return int(
        round(
            beat
            * ticks_per_beat
        )
    )


# ============================================================
# 建立 MIDI
# ============================================================

def create_output_midi(
    original_mid,
    notes,
    output_path
):

    ticks_per_beat = (
        original_mid.ticks_per_beat
    )

    # --------------------------------------------------------
    # 建立 MIDI
    # --------------------------------------------------------

    out_mid = MidiFile(
        ticks_per_beat=ticks_per_beat
    )

    track = MidiTrack()

    out_mid.tracks.append(track)

    # --------------------------------------------------------
    # 收集 meta events
    # --------------------------------------------------------

    tempo = get_tempo(
        original_mid
    )

    numerator, denominator = (
        get_time_signature(
            original_mid
        )
    )

    # Tempo
    track.append(
        MetaMessage(
            "set_tempo",
            tempo=tempo,
            time=0
        )
    )

    # Time Signature
    track.append(
        MetaMessage(
            "time_signature",
            numerator=numerator,
            denominator=denominator,
            clocks_per_click=24,
            notated_32nd_notes_per_beat=8,
            time=0
        )
    )

    # --------------------------------------------------------
    # 將音符轉成 tick event
    # --------------------------------------------------------

    events = []

    for note in notes:

        start_tick = beat_to_tick(
            note.start,
            ticks_per_beat
        )

        end_tick = beat_to_tick(
            note.end,
            ticks_per_beat
        )

        if end_tick <= start_tick:

            continue

        events.append(
            (
                start_tick,
                1,
                note.pitch,
                note.velocity,
                note.channel
            )
        )

        events.append(
            (
                end_tick,
                0,
                note.pitch,
                0,
                note.channel
            )
        )

    # --------------------------------------------------------
    # 排序
    #
    # 同 tick：
    # note_off 優先
    # note_on 後面
    # --------------------------------------------------------

    events.sort(
        key=lambda x: (
            x[0],
            x[1]
        )
    )

    current_tick = 0

    for (
        tick,
        event_type,
        pitch,
        velocity,
        channel
    ) in events:

        delta = tick - current_tick

        if delta < 0:

            delta = 0

        if event_type == 0:

            msg = Message(
                "note_off",
                note=pitch,
                velocity=0,
                channel=channel,
                time=delta
            )

        else:

            msg = Message(
                "note_on",
                note=pitch,
                velocity=velocity,
                channel=channel,
                time=delta
            )

        track.append(msg)

        current_tick = tick

    # --------------------------------------------------------
    # 結尾
    # --------------------------------------------------------

    track.append(
        MetaMessage(
            "end_of_track",
            time=0
        )
    )

    # --------------------------------------------------------
    # 儲存
    # --------------------------------------------------------

    os.makedirs(
        os.path.dirname(
            os.path.abspath(output_path)
        ),
        exist_ok=True
    )

    out_mid.save(
        output_path
    )


# ============================================================
# Debug 顯示
# ============================================================

def print_statistics(
    title,
    notes
):

    if not notes:

        print(
            f"{title}: 0"
        )

        return

    durations = [
        n.duration
        for n in notes
    ]

    print(
        f"{title}: {len(notes)}"
    )

    print(
        f"  最低音: {min(n.pitch for n in notes)}"
    )

    print(
        f"  最高音: {max(n.pitch for n in notes)}"
    )

    print(
        f"  最短: {min(durations):.4f}"
    )

    print(
        f"  最長: {max(durations):.4f}"
    )


# ============================================================
# 主流程
# ============================================================

def process_midi(
    input_path,
    output_path
):

    print("=" * 60)
    print("JianpuTool Melody Clean + Quantize")
    print("★ Cross-Measure Fix")
    print("=" * 60)

    print()
    print(f"輸入：{input_path}")
    print(f"輸出：{output_path}")
    print()

    # --------------------------------------------------------
    # 1. 讀取 MIDI
    # --------------------------------------------------------

    print("[1/9] 讀取 MIDI")

    mid = MidiFile(
        input_path
    )

    print(
        f"  ticks_per_beat = "
        f"{mid.ticks_per_beat}"
    )

    # --------------------------------------------------------
    # Time Signature
    # --------------------------------------------------------

    numerator, denominator = (
        get_time_signature(mid)
    )

    print(
        f"  拍號 = "
        f"{numerator}/{denominator}"
    )

    tempo = get_tempo(mid)

    bpm = (
        60_000_000
        / tempo
    )

    print(
        f"  BPM = {bpm:.2f}"
    )

    # --------------------------------------------------------
    # 2. Extract
    # --------------------------------------------------------

    print()
    print("[2/9] 擷取旋律音符")

    notes = extract_melody(mid)

    print_statistics(
        "  原始音符",
        notes
    )

    # --------------------------------------------------------
    # 3. Pitch filter
    # --------------------------------------------------------

    print()
    print("[3/9] 音域過濾")

    notes = filter_pitch_range(
        notes
    )

    print_statistics(
        "  音域過濾後",
        notes
    )

    # --------------------------------------------------------
    # 4. Remove short
    # --------------------------------------------------------

    print()
    print("[4/9] 移除過短音符")

    notes = remove_short_notes(
        notes
    )

    print_statistics(
        "  過短音符移除後",
        notes
    )

    # --------------------------------------------------------
    # 5. Monophonic
    # --------------------------------------------------------

    print()
    print("[5/9] 單音旋律清理")

    if MONOPHONIC:

        notes = make_monophonic(
            notes
        )

        notes = fix_overlaps(
            notes
        )

    print_statistics(
        "  單音化後",
        notes
    )

    # --------------------------------------------------------
    # 6. Quantize
    # --------------------------------------------------------

    print()
    print("[6/9] 1/16 拍量化")

    notes = quantize_notes(
        notes
    )

    notes = sort_notes(
        notes
    )

    print_statistics(
        "  量化後",
        notes
    )

    # --------------------------------------------------------
    # 7. ★ Cross measure split
    # --------------------------------------------------------

    print()
    print("[7/9] ★ 修正跨小節音符")

    before_split = len(notes)

    notes = split_notes_at_barlines(
        notes,
        numerator,
        denominator
    )

    after_split = len(notes)

    print(
        f"  原本音符數：{before_split}"
    )

    print(
        f"  切割後音符數：{after_split}"
    )

    print(
        f"  新增切割音符："
        f"{after_split - before_split}"
    )

    # --------------------------------------------------------
    # 8. Final validation
    # --------------------------------------------------------

    print()
    print("[8/9] 最終小節檢查")

    notes = remove_tiny_segments(
        notes
    )

    errors = validate_bar_boundaries(
        notes,
        numerator,
        denominator
    )

    if errors:

        print(
            f"  ❌ 發現 {len(errors)} 個跨小節問題"
        )

        # ----------------------------------------------------
        # 再修一次
        # ----------------------------------------------------

        notes = split_notes_at_barlines(
            notes,
            numerator,
            denominator
        )

        errors = validate_bar_boundaries(
            notes,
            numerator,
            denominator
        )

    if errors:

        print(
            "  ❌ 仍然存在跨小節音符"
        )

        for error in errors[:10]:

            index, error_type, note = error

            print(
                f"    {index}: "
                f"{error_type} "
                f"{note}"
            )

        raise RuntimeError(
            "MIDI 跨小節修正失敗"
        )

    else:

        print(
            "  ✅ 所有音符均位於合法小節範圍"
        )

    # --------------------------------------------------------
    # 不合併跨小節
    # --------------------------------------------------------

    notes = merge_adjacent_same_pitch(
        notes,
        numerator,
        denominator
    )

    # merge 後再次 split
    notes = split_notes_at_barlines(
        notes,
        numerator,
        denominator
    )

    # --------------------------------------------------------
    # 最終排序
    # --------------------------------------------------------

    notes = sort_notes(
        notes
    )

    # --------------------------------------------------------
    # 9. Output
    # --------------------------------------------------------

    print()
    print("[9/9] 建立乾淨 MIDI")

    create_output_midi(
        mid,
        notes,
        output_path
    )

    # --------------------------------------------------------
    # 最終檢查
    # --------------------------------------------------------

    check_mid = MidiFile(
        output_path
    )

    check_notes = extract_melody(
        check_mid
    )

    final_errors = (
        validate_bar_boundaries(
            check_notes,
            numerator,
            denominator
        )
    )

    print()
    print("=" * 60)

    if final_errors:

        print(
            "❌ 最終 MIDI 檢查失敗"
        )

        print(
            f"跨小節錯誤："
            f"{len(final_errors)}"
        )

        raise RuntimeError(
            "輸出的 MIDI 仍存在跨小節問題"
        )

    print(
        "🎉 完成！"
    )

    print(
        f"最終音符數："
        f"{len(check_notes)}"
    )

    print(
        "✅ 無跨小節音符"
    )

    print(
        "✅ 1/16 拍量化"
    )

    print(
        "✅ 單音旋律"
    )

    print(
        "✅ 可交給 MusicXML 轉換"
    )

    print(
        f"輸出：{output_path}"
    )

    print("=" * 60)

    return output_path


# ============================================================
# CLI
# ============================================================

def main():

    if len(sys.argv) < 3:

        print()
        print(
            "用法："
        )

        print(
            "python melody_clean_quantize.py "
            "input.mid output.mid"
        )

        print()

        print(
            "例如："
        )

        print(
            "python melody_clean_quantize.py "
            "raw_melody.mid vocal_clean.mid"
        )

        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    if not os.path.isfile(input_path):

        print(
            f"❌ 找不到輸入 MIDI："
            f"{input_path}"
        )

        sys.exit(1)

    try:

        process_midi(
            input_path,
            output_path
        )

    except Exception as e:

        print()
        print(
            "❌ 處理失敗："
        )

        print(
            str(e)
        )

        raise


# ============================================================
# Entry
# ============================================================

if __name__ == "__main__":

    main()