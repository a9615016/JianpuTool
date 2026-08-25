import sys
import json
import os
import copy

from music21 import (
    converter,
    stream,
    meter,
    key as m21key,
    note,
    chord,
)


# ============================================================
# JianpuTool
# MIDI -> MusicXML
#
# 目的：
# 1. 保留 MIDI 原始 offset
# 2. 強制 4/4
# 3. 所有 Note / Rest 不得跨小節
# 4. 跨小節音符自動切割
# 5. 自動建立 tie
# 6. 寫出後重新讀取驗證
#
# 適合：
# MIDI -> MusicXML -> jianpu-ly -> LilyPond
# ============================================================


TIME_SIGNATURE = "4/4"
BAR_LENGTH = 4.0

# ============================================================
# 讀取調性
# ============================================================

def load_key(info_json):

    if not info_json or not os.path.isfile(info_json):

        print(
            "⚠ 找不到 info.json，"
            "MusicXML 調號預設為 C major"
        )

        return m21key.Key("C", "major")

    try:

        with open(
            info_json,
            "r",
            encoding="utf-8"
        ) as f:

            info = json.load(f)

    except Exception as e:

        print(
            "⚠ 讀取 info.json 失敗:",
            e
        )

        return m21key.Key("C", "major")

    tonic = info.get(
        "key_tonic",
        "C"
    )

    mode = info.get(
        "key_mode",
        "major"
    )

    print(
        f"✓ 套用偵測到的調性: "
        f"{tonic} {mode}"
    )

    try:

        return m21key.Key(
            tonic,
            mode
        )

    except Exception:

        print(
            "⚠ 調性無法解析，"
            "改用 C major"
        )

        return m21key.Key(
            "C",
            "major"
        )


# ============================================================
# 複製 Note / Rest
# ============================================================

def clone_element(element):

    try:
        return copy.deepcopy(element)
    except Exception:
        return element


# ============================================================
# 將單一 Note / Rest 切成不跨小節的片段
# ============================================================

def split_element_at_bars(element, absolute_offset):

    """
    將一個 Note / Rest 切成多個片段。

    例如：

        offset = 3.5
        duration = 1.0

    會變成：

        3.5 ~ 4.0
        4.0 ~ 4.5

    並建立 tie。
    """

    duration = float(
        element.duration.quarterLength
    )

    if duration <= 0:
        return []

    start = float(absolute_offset)
    end = start + duration

    pieces = []

    current = start

    while current < end - 1e-9:

        # ----------------------------------------------------
        # 下一個小節線
        # ----------------------------------------------------

        next_bar = (
            (int(current // BAR_LENGTH) + 1)
            * BAR_LENGTH
        )

        piece_end = min(
            end,
            next_bar
        )

        piece_duration = (
            piece_end - current
        )

        if piece_duration <= 1e-9:
            break

        new_element = clone_element(
            element
        )

        new_element.duration = (
            element.duration.__class__(
                quarterLength=piece_duration
            )
        )

        # ----------------------------------------------------
        # 建立 tie
        # ----------------------------------------------------

        is_first = (
            abs(current - start) < 1e-9
        )

        is_last = (
            abs(piece_end - end) < 1e-9
        )

        if isinstance(
            new_element,
            note.Note
        ):

            if not is_first and not is_last:

                new_element.tie = note.Tie(
                    "continue"
                )

            elif not is_first:

                new_element.tie = note.Tie(
                    "stop"
                )

            elif not is_last:

                new_element.tie = note.Tie(
                    "start"
                )

        pieces.append(
            (
                current,
                new_element
            )
        )

        current = piece_end

    return pieces


# ============================================================
# 展開 Chord
# ============================================================

def chord_to_notes(element):

    if not isinstance(
        element,
        chord.Chord
    ):

        return [element]

    result = []

    for pitch in element.pitches:

        n = note.Note(
            pitch
        )

        n.duration = (
            element.duration
        )

        result.append(
            n
        )

    return result


# ============================================================
# 建立新的 Part
# ============================================================

def build_part(
    original_part,
    detected_key
):

    p = stream.Part()

    # --------------------------------------------------------
    # 4/4
    # --------------------------------------------------------

    p.insert(
        0,
        meter.TimeSignature(
            TIME_SIGNATURE
        )
    )

    # --------------------------------------------------------
    # 調性
    # --------------------------------------------------------

    p.insert(
        0,
        detected_key
    )

    # --------------------------------------------------------
    # 收集 MIDI 元素
    # --------------------------------------------------------

    original_elements = list(
        original_part.recurse().notesAndRests
    )

    print(
        f"原始 Note/Rest 數量："
        f"{len(original_elements)}"
    )

    output_count = 0
    split_count = 0

    # --------------------------------------------------------
    # 每個元素重新建立
    # --------------------------------------------------------

    for element in original_elements:

        try:

            absolute_offset = float(
                element.getOffsetInHierarchy(
                    original_part
                )
            )

        except Exception:

            absolute_offset = float(
                element.offset
            )

        # ----------------------------------------------------
        # Chord 拆成單音
        # ----------------------------------------------------

        elements_to_process = (
            chord_to_notes(element)
        )

        for source_element in elements_to_process:

            pieces = split_element_at_bars(
                source_element,
                absolute_offset
            )

            if len(pieces) > 1:

                split_count += (
                    len(pieces) - 1
                )

            # ------------------------------------------------
            # 插入
            # ------------------------------------------------

            for piece_offset, piece in pieces:

                # ------------------------------------------------
                # 確保 offset 不會落在負數
                # ------------------------------------------------

                if piece_offset < 0:

                    piece_offset = 0.0

                p.insert(
                    piece_offset,
                    piece
                )

                output_count += 1

    print(
        f"輸出 Note/Rest 數量："
        f"{output_count}"
    )

    print(
        f"跨小節切割數量："
        f"{split_count}"
    )

    return p


# ============================================================
# 清理小節
# ============================================================

def rebuild_measures(score):

    print(
        "建立 4/4 小節..."
    )

    # --------------------------------------------------------
    # 第一次 makeMeasures
    # --------------------------------------------------------

    score = score.makeMeasures(
        inPlace=False
    )

    return score


# ============================================================
# 深度檢查
# ============================================================

def validate_no_cross_bar(score):

    print()
    print(
        "檢查 MusicXML 前置結構..."
    )

    errors = []

    for part_index, part in enumerate(
        score.parts
    ):

        measures = part.getElementsByClass(
            stream.Measure
        )

        for measure in measures:

            measure_number = (
                measure.number
            )

            measure_length = (
                float(
                    measure.barDuration.quarterLength
                )
                if measure.barDuration
                else BAR_LENGTH
            )

            for element in measure.notesAndRests:

                offset = float(
                    element.offset
                )

                duration = float(
                    element.duration.quarterLength
                )

                end = offset + duration

                if end > measure_length + 1e-6:

                    kind = (
                        "NOTE"
                        if isinstance(
                            element,
                            note.Note
                        )
                        else "REST"
                    )

                    errors.append(
                        (
                            part_index + 1,
                            measure_number,
                            kind,
                            offset,
                            duration,
                            end,
                            measure_length
                        )
                    )

                    print(
                        f"❌ Part {part_index + 1} "
                        f"Measure {measure_number} "
                        f"{kind}: "
                        f"offset={offset:.4f} "
                        f"duration={duration:.4f} "
                        f"end={end:.4f}"
                    )

    if errors:

        print()
        print(
            f"❌ 發現跨小節元素："
            f"{len(errors)} 個"
        )

        return False

    print(
        "✅ 深度驗證：沒有跨小節音符"
    )

    return True


# ============================================================
# 寫出後重新驗證 MusicXML
# ============================================================

def validate_written_musicxml(
    output_xml
):

    print()
    print(
        "重新讀取 MusicXML 驗證..."
    )

    try:

        test_score = converter.parse(
            output_xml
        )

    except Exception as e:

        raise RuntimeError(
            "MusicXML 重新讀取失敗："
            + str(e)
        )

    errors = []

    for part_index, part in enumerate(
        test_score.parts
    ):

        for measure in part.getElementsByClass(
            stream.Measure
        ):

            measure_length = (
                float(
                    measure.barDuration.quarterLength
                )
                if measure.barDuration
                else BAR_LENGTH
            )

            for element in measure.notesAndRests:

                offset = float(
                    element.offset
                )

                duration = float(
                    element.duration.quarterLength
                )

                end = offset + duration

                if end > measure_length + 1e-6:

                    kind = (
                        "NOTE"
                        if isinstance(
                            element,
                            note.Note
                        )
                        else "REST"
                    )

                    errors.append(
                        (
                            part_index + 1,
                            measure.number,
                            kind,
                            offset,
                            duration,
                            end
                        )
                    )

                    print(
                        f"❌ Part {part_index + 1} "
                        f"Measure {measure.number} "
                        f"{kind}: "
                        f"offset={offset:.4f} "
                        f"duration={duration:.4f} "
                        f"end={end:.4f}"
                    )

    if errors:

        raise RuntimeError(
            "MusicXML 寫出後仍存在跨小節元素："
            f"{len(errors)} 個"
        )

    print(
        "✅ MusicXML 深度驗證："
        "沒有跨小節音符"
    )


# ============================================================
# MIDI -> MusicXML
# ============================================================

def convert(
    input_midi,
    output_xml,
    info_json=None
):

    print()
    print(
        "========================================"
    )
    print(
        "MIDI -> MusicXML"
    )
    print(
        "========================================"
    )

    print(
        "輸入 MIDI:",
        input_midi
    )

    print(
        "輸出 MusicXML:",
        output_xml
    )

    # --------------------------------------------------------
    # 檢查 MIDI
    # --------------------------------------------------------

    if not os.path.isfile(
        input_midi
    ):

        raise FileNotFoundError(
            f"找不到 MIDI: {input_midi}"
        )

    # --------------------------------------------------------
    # 建立輸出資料夾
    # --------------------------------------------------------

    output_dir = os.path.dirname(
        os.path.abspath(
            output_xml
        )
    )

    os.makedirs(
        output_dir,
        exist_ok=True
    )

    # --------------------------------------------------------
    # 讀取 MIDI
    # --------------------------------------------------------

    print(
        "讀取 MIDI..."
    )

    score = converter.parse(
        input_midi
    )

    print(
        f"✓ Parts: {len(score.parts)}"
    )

    # --------------------------------------------------------
    # 調性
    # --------------------------------------------------------

    detected_key = load_key(
        info_json
    )

    # --------------------------------------------------------
    # 建立新 Score
    # --------------------------------------------------------

    new_score = stream.Score()

    # --------------------------------------------------------
    # 逐 Part
    # --------------------------------------------------------

    for index, part in enumerate(
        score.parts
    ):

        print(
            f"處理 Part {index + 1}..."
        )

        new_part = build_part(
            part,
            detected_key
        )

        new_score.insert(
            0,
            new_part
        )

    # --------------------------------------------------------
    # 前置驗證
    # --------------------------------------------------------

    new_score = rebuild_measures(
        new_score
    )

    # --------------------------------------------------------
    # 再次驗證
    # --------------------------------------------------------

    if not validate_no_cross_bar(
        new_score
    ):

        raise RuntimeError(
            "MusicXML 前置結構仍有跨小節元素"
        )

    # --------------------------------------------------------
    # 確保每個 Part 有 4/4
    # --------------------------------------------------------

    for part in new_score.parts:

        time_signatures = (
            part.recurse()
            .getElementsByClass(
                meter.TimeSignature
            )
        )

        if not time_signatures:

            part.insert(
                0,
                meter.TimeSignature(
                    TIME_SIGNATURE
                )
            )

        keys = (
            part.recurse()
            .getElementsByClass(
                m21key.Key
            )
        )

        if not keys:

            part.insert(
                0,
                detected_key
            )

    # --------------------------------------------------------
    # 寫入 MusicXML
    # --------------------------------------------------------

    print(
        "寫入 MusicXML..."
    )

    new_score.write(
        "musicxml",
        fp=output_xml
    )

    # --------------------------------------------------------
    # 確認檔案
    # --------------------------------------------------------

    if not os.path.isfile(
        output_xml
    ):

        raise RuntimeError(
            "MusicXML 產生失敗"
        )

    size = os.path.getsize(
        output_xml
    )

    print(
        "✓ MusicXML 完成"
    )

    print(
        f"✓ 檔案大小: {size:,} bytes"
    )

    # --------------------------------------------------------
    # 寫出後重新讀取驗證
    # --------------------------------------------------------

    validate_written_musicxml(
        output_xml
    )

    print(
        "========================================"
    )


# ============================================================
# CMD
# ============================================================

if __name__ == "__main__":

    if len(sys.argv) < 3:

        print()
        print(
            "用法:"
        )

        print(
            "python midi_to_musicxml.py "
            "input.mid output.musicxml [info.json]"
        )

        print()

        sys.exit(1)

    input_midi = sys.argv[1]

    output_xml = sys.argv[2]

    info_json = (
        sys.argv[3]
        if len(sys.argv) > 3
        else None
    )

    try:

        convert(
            input_midi,
            output_xml,
            info_json
        )

    except Exception as e:

        print()
        print(
            "❌ MIDI -> MusicXML 失敗"
        )

        print(
            str(e)
        )

        sys.exit(1)