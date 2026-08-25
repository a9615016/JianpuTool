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
)


# ============================================================
# 基本設定
# ============================================================

MEASURE_LENGTH = 4.0


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
# 安全複製 Note / Rest
# ============================================================

def clone_element(element):

    try:
        return copy.deepcopy(element)
    except Exception:
        try:
            return element.clone()
        except Exception:
            return copy.copy(element)


# ============================================================
# 切割單一音符 / Rest
#
# 例如：
#
# offset = 3.5
# duration = 1.0
#
# 4/4 小節線在 4.0
#
# 原本：
#
# 3.5 ───────── 4.5
#
# 修正：
#
# 3.5 ─── 4.0
# 4.0 ─── 4.5
#
# 並加 tie。
# ============================================================

def split_element_at_barlines(element, absolute_offset):

    duration = float(
        element.duration.quarterLength
    )

    if duration <= 0:
        return [
            (
                absolute_offset,
                clone_element(element)
            )
        ]

    end = absolute_offset + duration

    # 沒有跨小節
    first_bar = int(
        absolute_offset // MEASURE_LENGTH
    )

    last_bar = int(
        (end - 1e-9) // MEASURE_LENGTH
    )

    if first_bar == last_bar:

        return [
            (
                absolute_offset,
                clone_element(element)
            )
        ]

    print(
        f"    ✂ 切割跨小節音符:"
        f" {absolute_offset:.4f}"
        f" → {end:.4f}"
    )

    result = []

    current_start = absolute_offset
    remaining = duration

    first_piece = True

    while remaining > 1e-9:

        next_barline = (
            (int(current_start // MEASURE_LENGTH) + 1)
            * MEASURE_LENGTH
        )

        available = next_barline - current_start

        piece_length = min(
            remaining,
            available
        )

        piece = clone_element(element)

        piece.duration.quarterLength = (
            piece_length
        )

        # ----------------------------------------------------
        # tie
        # ----------------------------------------------------

        if hasattr(piece, "tie"):

            if remaining - piece_length > 1e-9:

                # 還有下一段
                piece.tie = note.Tie(
                    "start"
                )

            elif not first_piece:

                # 最後一段
                piece.tie = note.Tie(
                    "stop"
                )

        result.append(
            (
                current_start,
                piece
            )
        )

        current_start += piece_length
        remaining -= piece_length

        first_piece = False

    # --------------------------------------------------------
    # 修正 tie：
    #
    # 第一段 start
    # 中間段 continue
    # 最後 stop
    # --------------------------------------------------------

    if len(result) > 1:

        for i, (_, piece) in enumerate(result):

            if not hasattr(piece, "tie"):
                continue

            if i == 0:

                piece.tie = note.Tie(
                    "start"
                )

            elif i == len(result) - 1:

                piece.tie = note.Tie(
                    "stop"
                )

            else:

                piece.tie = note.Tie(
                    "continue"
                )

    return result


# ============================================================
# 建立新的 Part
# ============================================================

def build_part(original_part, detected_key):

    p = stream.Part()

    # --------------------------------------------------------
    # 4/4
    # --------------------------------------------------------

    p.insert(
        0,
        meter.TimeSignature("4/4")
    )

    # --------------------------------------------------------
    # 調性
    # --------------------------------------------------------

    p.insert(
        0,
        clone_element(detected_key)
    )

    # --------------------------------------------------------
    # 收集原始 Note / Rest
    # --------------------------------------------------------

    elements = list(
        original_part.recurse().notesAndRests
    )

    if not elements:
        return p

    print(
        f"原始 Note/Rest 數量：{len(elements)}"
    )

    # --------------------------------------------------------
    # 明確按照 absolute offset 建立
    # --------------------------------------------------------

    split_count = 0
    output_count = 0

    for element in elements:

        # ----------------------------------------------------
        # 取得 element 在 original_part 的絕對 offset
        # ----------------------------------------------------

        try:

            offset = float(
                element.getOffsetInHierarchy(
                    original_part
                )
            )

        except Exception:

            offset = float(
                element.offset
            )

        # ----------------------------------------------------
        # 只處理 Note / Rest
        # ----------------------------------------------------

        if not (
            element.isNote
            or element.isRest
        ):
            continue

        # ----------------------------------------------------
        # 切割跨小節音符
        # ----------------------------------------------------

        pieces = split_element_at_barlines(
            element,
            offset
        )

        if len(pieces) > 1:
            split_count += 1

        # ----------------------------------------------------
        # 插入
        # ----------------------------------------------------

        for piece_offset, piece in pieces:

            p.insert(
                piece_offset,
                piece
            )

            output_count += 1

    print(
        f"輸出 Note/Rest 數量：{output_count}"
    )

    print(
        f"跨小節切割數量：{split_count}"
    )

    return p


# ============================================================
# 最終 MusicXML 跨小節驗證
#
# 注意：
# 這裡驗證的是 music21 Score。
# 真正寫檔後還會再次解析 MusicXML。
# ============================================================

def validate_score_no_cross_barline(score):

    print()
    print(
        "檢查 MusicXML 前置結構..."
    )

    error_count = 0

    for part_index, part in enumerate(
        score.parts,
        start=1
    ):

        notes = list(
            part.recurse().notesAndRests
        )

        for element in notes:

            try:

                offset = float(
                    element.getOffsetInHierarchy(
                        part
                    )
                )

            except Exception:

                offset = float(
                    element.offset
                )

            duration = float(
                element.duration.quarterLength
            )

            if duration <= 0:
                continue

            end = offset + duration

            start_bar = int(
                offset // MEASURE_LENGTH
            )

            end_bar = int(
                (end - 1e-9)
                // MEASURE_LENGTH
            )

            if start_bar != end_bar:

                error_count += 1

                print(
                    f"❌ Part {part_index}: "
                    f"跨小節 "
                    f"{offset:.4f} → {end:.4f}"
                )

    if error_count == 0:

        print(
            "✅ 前置結構檢查：無跨小節音符"
        )

    else:

        raise RuntimeError(
            f"發現 {error_count} 個跨小節音符"
        )


# ============================================================
# 重新解析輸出的 MusicXML
#
# 這一步非常重要。
#
# 因為：
#
# music21 Score 正常
#      ↓
# MusicXML exporter
#      ↓
# exporter 可能重新處理 duration
#
# 所以寫檔後必須再讀一次。
# ============================================================

def validate_written_musicxml(output_xml):

    print()
    print(
        "重新讀取 MusicXML 驗證..."
    )

    check_score = converter.parse(
        output_xml
    )

    error_count = 0

    for part_index, part in enumerate(
        check_score.parts,
        start=1
    ):

        # ----------------------------------------------------
        # 建立 measure
        # ----------------------------------------------------

        measured_part = part.makeMeasures(
            inPlace=False
        )

        for measure in measured_part.getElementsByClass(
            stream.Measure
        ):

            measure_number = (
                measure.measureNumber
            )

            # ------------------------------------------------
            # 小節內 offset
            # ------------------------------------------------

            for element in measure.notesAndRests:

                duration = float(
                    element.duration.quarterLength
                )

                if duration <= 0:
                    continue

                local_offset = float(
                    element.offset
                )

                end = (
                    local_offset
                    + duration
                )

                # ------------------------------------------------
                # 4/4 小節不能超過 4
                # ------------------------------------------------

                if end > MEASURE_LENGTH + 1e-7:

                    error_count += 1

                    kind = (
                        "REST"
                        if element.isRest
                        else "NOTE"
                    )

                    print(
                        f"❌ Part {part_index} "
                        f"Measure {measure_number} "
                        f"{kind}: "
                        f"offset={local_offset:.4f} "
                        f"duration={duration:.4f} "
                        f"end={end:.4f}"
                    )

    if error_count > 0:

        raise RuntimeError(
            "MusicXML 寫出後仍存在跨小節音符："
            f"{error_count} 個"
        )

    print(
        "✅ MusicXML 深度驗證："
        "沒有跨小節音符"
    )


# ============================================================
# MusicXML 轉換
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
    # 建立新的 Score
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
    # 前置跨小節檢查
    # --------------------------------------------------------

    validate_score_no_cross_barline(
        new_score
    )

    # --------------------------------------------------------
    # 建立 4/4 小節
    # --------------------------------------------------------

    print(
        "建立 4/4 小節..."
    )

    new_score = new_score.makeMeasures(
        inPlace=False
    )

    # --------------------------------------------------------
    # 再檢查一次
    # --------------------------------------------------------

    print(
        "檢查 makeMeasures 後的結構..."
    )

    validate_score_no_cross_barline(
        new_score
    )

    # --------------------------------------------------------
    # 確保 TimeSignature
    # --------------------------------------------------------

    for part in new_score.parts:

        existing_ts = (
            part.recurse()
            .getElementsByClass(
                meter.TimeSignature
            )
        )

        if not existing_ts:

            part.insert(
                0,
                meter.TimeSignature("4/4")
            )

        existing_keys = (
            part.recurse()
            .getElementsByClass(
                m21key.Key
            )
        )

        if not existing_keys:

            part.insert(
                0,
                clone_element(detected_key)
            )

    # --------------------------------------------------------
    # 儲存
    # --------------------------------------------------------

    print(
        "寫入 MusicXML..."
    )

    new_score.write(
        "musicxml",
        fp=output_xml
    )

    # --------------------------------------------------------
    # 確認輸出
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
        f"✓ MusicXML 完成"
    )

    print(
        f"✓ 檔案大小: {size:,} bytes"
    )

    # --------------------------------------------------------
    # 寫出後再次解析驗證
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

        print(
            "用法:"
        )

        print(
            "python midi_to_musicxml.py "
            "input.mid output.musicxml [info.json]"
        )

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