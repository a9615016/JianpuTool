import sys
import os
import math

from mido import MidiFile, MidiTrack, Message, MetaMessage


# ============================================================
# JianpuTool Professional MVP 3.0
#
# melody_clean_quantize.py
#
# 功能：
#
# MIDI
#   ↓
# 單音旋律清理
#   ↓
# 音域限制
#   ↓
# 1/16 拍量化
#   ↓
# 4/4 小節邊界切割
#   ↓
# 移除過短音符
#   ↓
# 消除同時多音
#   ↓
# 產生乾淨 MIDI
#
# 重要：
# 不允許任何 Note 跨越 4/4 小節線。
# ============================================================


# ============================================================
# 基本設定
# ============================================================

TICKS_PER_BEAT = 480

BEATS_PER_BAR = 4

BAR_TICKS = TICKS_PER_BEAT * BEATS_PER_BAR

# 1/16 拍
GRID_TICKS = TICKS_PER_BEAT // 4

# 最短音符
MIN_NOTE_TICKS = GRID_TICKS

# 合理人聲音域
MIN_NOTE = 48       # C3
MAX_NOTE = 84       # C6

# 同時間多音時，最多保留一個
MONOPHONIC = True


# ============================================================
# 工具
# ============================================================

def clamp(value, minimum, maximum):

    return max(
        minimum,
        min(
            maximum,
            value
        )
    )


def quantize_tick(tick):

    if tick <= 0:
        return 0

    return int(
        round(
            tick / GRID_TICKS
        ) * GRID_TICKS
    )


# ============================================================
# MIDI Note 結構
# ============================================================

class NoteEvent:

    def __init__(
        self,
        note,
        start,
        end,
        velocity=80,
        channel=0
    ):

        self.note = int(note)

        self.start = int(start)

        self.end = int(end)

        self.velocity = int(
            clamp(
                velocity,
                1,
                127
            )
        )

        self.channel = int(channel)

    @property
    def duration(self):

        return self.end - self.start

    def __repr__(self):

        return (
            f"NoteEvent("
            f"note={self.note}, "
            f"start={self.start}, "
            f"end={self.end}, "
            f"duration={self.duration}"
            f")"
        )


# ============================================================
# 讀取 MIDI
# ============================================================

def read_midi(input_file):

    print()
    print("讀取 MIDI...")
    print(
        "輸入:",
        input_file
    )

    midi = MidiFile(input_file)

    print(
        f"✓ ticks_per_beat: "
        f"{midi.ticks_per_beat}"
    )

    events = []

    # --------------------------------------------------------
    # 如果不是 480，後面全部轉換成 480
    # --------------------------------------------------------

    source_tpb = midi.ticks_per_beat

    for track_index, track in enumerate(
        midi.tracks
    ):

        absolute_tick = 0

        active_notes = {}

        for msg in track:

            absolute_tick += msg.time

            # ------------------------------------------------
            # Note On
            # ------------------------------------------------

            if (
                msg.type == "note_on"
                and msg.velocity > 0
            ):

                key = (
                    msg.channel,
                    msg.note
                )

                active_notes[key] = (
                    absolute_tick,
                    msg.velocity
                )

            # ------------------------------------------------
            # Note Off
            # ------------------------------------------------

            elif (
                msg.type == "note_off"
                or (
                    msg.type == "note_on"
                    and msg.velocity == 0
                )
            ):

                key = (
                    msg.channel,
                    msg.note
                )

                if key not in active_notes:
                    continue

                start, velocity = active_notes.pop(
                    key
                )

                end = absolute_tick

                # --------------------------------------------
                # 轉成 480 TPB
                # --------------------------------------------

                if source_tpb != TICKS_PER_BEAT:

                    start = int(
                        round(
                            start
                            * TICKS_PER_BEAT
                            / source_tpb
                        )
                    )

                    end = int(
                        round(
                            end
                            * TICKS_PER_BEAT
                            / source_tpb
                        )
                    )

                if end > start:

                    events.append(
                        NoteEvent(
                            note=msg.note,
                            start=start,
                            end=end,
                            velocity=velocity,
                            channel=msg.channel
                        )
                    )

    print(
        f"✓ 原始音符數量：{len(events)}"
    )

    return events


# ============================================================
# 音域過濾
# ============================================================

def filter_pitch_range(events):

    print()
    print("檢查人聲音域...")

    result = []

    removed = 0

    for event in events:

        if (
            event.note < MIN_NOTE
            or
            event.note > MAX_NOTE
        ):

            removed += 1

            continue

        result.append(event)

    print(
        f"✓ 保留：{len(result)}"
    )

    print(
        f"✓ 移除過低/過高：{removed}"
    )

    return result


# ============================================================
# Quantize
# ============================================================

def quantize_events(events):

    print()
    print("1/16 拍量化...")

    result = []

    for event in events:

        start = quantize_tick(
            event.start
        )

        end = quantize_tick(
            event.end
        )

        # ----------------------------------------------------
        # 避免量化後 duration = 0
        # ----------------------------------------------------

        if end <= start:

            end = (
                start
                + MIN_NOTE_TICKS
            )

        # ----------------------------------------------------
        # 最短音符
        # ----------------------------------------------------

        if (
            end - start
            < MIN_NOTE_TICKS
        ):

            end = (
                start
                + MIN_NOTE_TICKS
            )

        result.append(
            NoteEvent(
                note=event.note,
                start=start,
                end=end,
                velocity=event.velocity,
                channel=event.channel
            )
        )

    result.sort(
        key=lambda x: (
            x.start,
            x.note
        )
    )

    print(
        f"✓ 量化完成：{len(result)}"
    )

    return result


# ============================================================
# 單音旋律
#
# 同一時間有多個音：
#
# 優先：
# 1. duration 長
# 2. velocity 高
#
# ============================================================

def make_monophonic(events):

    if not MONOPHONIC:

        return events

    print()
    print("建立單音旋律...")

    events = sorted(
        events,
        key=lambda x: (
            x.start,
            -(x.duration),
            -x.velocity
        )
    )

    result = []

    for event in events:

        # ----------------------------------------------------
        # 找最後一個保留音
        # ----------------------------------------------------

        if not result:

            result.append(
                event
            )

            continue

        previous = result[-1]

        # ----------------------------------------------------
        # 完全相同開始時間
        # ----------------------------------------------------

        if event.start == previous.start:

            # duration 長的留下
            if event.duration > previous.duration:

                result[-1] = event

            elif (
                event.duration
                == previous.duration
                and
                event.velocity
                > previous.velocity
            ):

                result[-1] = event

            continue

        # ----------------------------------------------------
        # 發生重疊
        # ----------------------------------------------------

        if event.start < previous.end:

            previous.end = event.start

            # 太短就移除
            if previous.duration < MIN_NOTE_TICKS:

                result.pop()

            result.append(
                event
            )

        else:

            result.append(
                event
            )

    print(
        f"✓ 單音旋律：{len(result)}"
    )

    return result


# ============================================================
# 重新計算音符
#
# 關鍵：
#
# 任何 Note 都不能跨越：
#
# 0
# 1920
# 3840
# 5760
# ...
#
# ============================================================

def split_at_barlines(events):

    print()
    print("切割跨 4/4 小節音符...")

    result = []

    split_count = 0

    for event in events:

        start = event.start

        end = event.end

        # ----------------------------------------------------
        # 防止非法
        # ----------------------------------------------------

        if end <= start:

            continue

        current = start

        while current < end:

            # ------------------------------------------------
            # 找目前所在小節結束位置
            # ------------------------------------------------

            bar_end = (
                (
                    current
                    // BAR_TICKS
                )
                + 1
            ) * BAR_TICKS

            segment_end = min(
                end,
                bar_end
            )

            duration = (
                segment_end
                - current
            )

            # ------------------------------------------------
            # 保留合法片段
            # ------------------------------------------------

            if duration > 0:

                result.append(
                    NoteEvent(
                        note=event.note,
                        start=current,
                        end=segment_end,
                        velocity=event.velocity,
                        channel=event.channel
                    )
                )

            # ------------------------------------------------
            # 發生跨小節
            # ------------------------------------------------

            if segment_end < end:

                split_count += 1

            current = segment_end

    print(
        f"✓ 跨小節切割：{split_count}"
    )

    print(
        f"✓ 切割後音符數量：{len(result)}"
    )

    return result


# ============================================================
# 第二次量化
#
# 切割後再次確保：
#
# start / end 都在 1/16 grid
# ============================================================

def final_grid_fix(events):

    print()
    print("最後 Grid 修正...")

    result = []

    for event in events:

        start = quantize_tick(
            event.start
        )

        end = quantize_tick(
            event.end
        )

        if end <= start:

            continue

        # ----------------------------------------------------
        # 最重要：
        #
        # 如果 end 剛好跨小節，
        # 強制切到小節線。
        # ----------------------------------------------------

        bar_end = (
            (
                start
                // BAR_TICKS
            )
            + 1
        ) * BAR_TICKS

        if end > bar_end:

            end = bar_end

        if end <= start:

            continue

        result.append(
            NoteEvent(
                note=event.note,
                start=start,
                end=end,
                velocity=event.velocity,
                channel=event.channel
            )
        )

    return result


# ============================================================
# 最終驗證
# ============================================================

def validate_events(events):

    print()
    print("========================================")
    print("最終 MIDI 結構驗證")
    print("========================================")

    errors = 0

    for index, event in enumerate(
        events
    ):

        if event.end <= event.start:

            print(
                f"❌ Note {index}: "
                f"duration <= 0"
            )

            errors += 1

            continue

        # ----------------------------------------------------
        # 小節線
        # ----------------------------------------------------

        bar_end = (
            (
                event.start
                // BAR_TICKS
            )
            + 1
        ) * BAR_TICKS

        if event.end > bar_end:

            print(
                f"❌ Note {index}: "
                f"跨小節 "
                f"start={event.start} "
                f"end={event.end} "
                f"bar_end={bar_end}"
            )

            errors += 1

        # ----------------------------------------------------
        # Grid
        # ----------------------------------------------------

        if (
            event.start
            % GRID_TICKS
            != 0
        ):

            print(
                f"❌ Note {index}: "
                f"start 不在 1/16 grid"
            )

            errors += 1

        if (
            event.end
            % GRID_TICKS
            != 0
        ):

            print(
                f"❌ Note {index}: "
                f"end 不在 1/16 grid"
            )

            errors += 1

    if errors:

        print()
        print(
            f"❌ 驗證失敗：{errors} 個問題"
        )

        raise RuntimeError(
            f"MIDI 結構驗證失敗：{errors} 個問題"
        )

    print(
        "✅ 沒有跨小節音符"
    )

    print(
        "✅ 所有音符符合 1/16 Grid"
    )

    print(
        "✅ MIDI 結構正常"
    )

    print(
        "========================================"
    )


# ============================================================
# 建立 MIDI
# ============================================================

def write_midi(
    events,
    output_file
):

    print()
    print("建立乾淨 MIDI...")

    midi = MidiFile(
        type=1,
        ticks_per_beat=TICKS_PER_BEAT
    )

    track = MidiTrack()

    midi.tracks.append(
        track
    )

    # --------------------------------------------------------
    # 4/4
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # 依照時間排序
    # --------------------------------------------------------

    midi_events = []

    for event in events:

        midi_events.append(
            (
                event.start,
                1,
                event
            )
        )

        midi_events.append(
            (
                event.end,
                0,
                event
            )
        )

    # --------------------------------------------------------
    # Note Off 優先
    # --------------------------------------------------------

    midi_events.sort(
        key=lambda x: (
            x[0],
            x[1]
        )
    )

    current_tick = 0

    for tick, event_type, event in midi_events:

        delta = (
            tick
            - current_tick
        )

        current_tick = tick

        if event_type == 1:

            track.append(
                Message(
                    "note_on",
                    note=event.note,
                    velocity=event.velocity,
                    channel=event.channel,
                    time=delta
                )
            )

        else:

            track.append(
                Message(
                    "note_off",
                    note=event.note,
                    velocity=0,
                    channel=event.channel,
                    time=delta
                )
            )

    # --------------------------------------------------------
    # End
    # --------------------------------------------------------

    track.append(
        MetaMessage(
            "end_of_track",
            time=0
        )
    )

    midi.save(
        output_file
    )

    if not os.path.isfile(
        output_file
    ):

        raise RuntimeError(
            "MIDI 寫入失敗"
        )

    size = os.path.getsize(
        output_file
    )

    print(
        f"✓ MIDI 完成：{output_file}"
    )

    print(
        f"✓ 檔案大小：{size:,} bytes"
    )


# ============================================================
# 主處理
# ============================================================

def clean_melody(
    input_file,
    output_file
):

    print()
    print(
        "============================================================"
    )

    print(
        "JianpuTool Professional MVP 3.0"
    )

    print(
        "Melody Clean + Quantize"
    )

    print(
        "============================================================"
    )

    # --------------------------------------------------------
    # 檢查輸入
    # --------------------------------------------------------

    if not os.path.isfile(
        input_file
    ):

        raise FileNotFoundError(
            f"找不到輸入 MIDI：{input_file}"
        )

    # --------------------------------------------------------
    # 1
    # --------------------------------------------------------

    events = read_midi(
        input_file
    )

    if not events:

        raise RuntimeError(
            "MIDI 沒有找到任何音符"
        )

    # --------------------------------------------------------
    # 2
    # --------------------------------------------------------

    events = filter_pitch_range(
        events
    )

    if not events:

        raise RuntimeError(
            "音域過濾後沒有剩餘音符"
        )

    # --------------------------------------------------------
    # 3
    # --------------------------------------------------------

    events = quantize_events(
        events
    )

    # --------------------------------------------------------
    # 4
    # --------------------------------------------------------

    events = make_monophonic(
        events
    )

    # --------------------------------------------------------
    # 5
    #
    # 關鍵修正
    # --------------------------------------------------------

    events = split_at_barlines(
        events
    )

    # --------------------------------------------------------
    # 6
    # --------------------------------------------------------

    events = final_grid_fix(
        events
    )

    # --------------------------------------------------------
    # 7
    #
    # 再次排序
    # --------------------------------------------------------

    events.sort(
        key=lambda x: (
            x.start,
            x.end,
            x.note
        )
    )

    # --------------------------------------------------------
    # 8
    #
    # 最終驗證
    # --------------------------------------------------------

    validate_events(
        events
    )

    # --------------------------------------------------------
    # 9
    #
    # 寫出 MIDI
    # --------------------------------------------------------

    write_midi(
        events,
        output_file
    )

    # --------------------------------------------------------
    # 統計
    # --------------------------------------------------------

    print()
    print(
        "============================================================"
    )

    print(
        "🎉 Melody Clean 完成"
    )

    print(
        "============================================================"
    )

    print(
        f"原始音符：{len(read_midi(input_file))}"
    )

    print(
        f"最終音符：{len(events)}"
    )

    print(
        f"音域：C3 ({MIN_NOTE}) ~ C6 ({MAX_NOTE})"
    )

    print(
        "量化：1/16 拍"
    )

    print(
        "拍號：4/4"
    )

    print(
        "跨小節音符：0"
    )

    print(
        f"輸出：{output_file}"
    )

    print(
        "============================================================"
    )

    return output_file


# ============================================================
# CMD
# ============================================================

if __name__ == "__main__":

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
            r"python melody_clean_quantize.py "
            r"outputs\test\raw_melody.mid "
            r"outputs\test\clean_melody.mid"
        )

        sys.exit(1)

    input_file = sys.argv[1]

    output_file = sys.argv[2]

    try:

        clean_melody(
            input_file,
            output_file
        )

    except Exception as e:

        print()
        print(
            "============================================================"
        )

        print(
            "❌ Melody Clean 失敗"
        )

        print(
            "============================================================"
        )

        print(
            str(e)
        )

        print(
            "============================================================"
        )

        sys.exit(1)