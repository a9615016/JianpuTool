import sys
import json
import os
import copy
import math

from music21 import converter, stream, meter, key as m21key
from music21 import note as m21note


# ============================================================
# JianpuTool Professional MVP 3.0
#
# MIDI -> MusicXML
#
# 核心目標：
# 1. 4/4
# 2. 1/16 拍量化
# 3. Note 不得跨小節
# 4. Rest 不得跨小節
# 5. 跨小節 Note 自動切割 + Tie
# 6. MusicXML 寫出後重新驗證
# 7. 最終必須 0 個跨小節元素
# 8. Windows / Linux / Streamlit Cloud
# ============================================================


TIME_SIGNATURE = "4/4"

MEASURE_LENGTH = 4.0

QUANTUM = 0.25


# ============================================================
# 調性
# ============================================================

def load_key(info_json):

    if not info_json or not os.path.isfile(info_json):

        print(
            "⚠ 找不到 info.json，"
            "預設 C major"
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
            "⚠ info.json 讀取失敗:",
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
            "⚠ 調性解析失敗，"
            "改用 C major"
        )

        return m21key.Key(
            "C",
            "major"
        )


# ============================================================
# 量化
# ============================================================

def quantize(value):

    value = float(value)

    return round(
        value / QUANTUM
    ) * QUANTUM


# ============================================================
# 安全長度
# ============================================================

def safe_duration(value):

    value = quantize(value)

    if value < QUANTUM:
        value = QUANTUM

    return value


# ============================================================
# 取得絕對 offset
# ============================================================

def get_absolute_offset(element, original_part):

    try:

        return float(
            element.getOffsetInHierarchy(
                original_part
            )
        )

    except Exception:

        return float(
            element.offset
        )


# ============================================================
# 複製元素
# ============================================================

def clone_element(element):

    try:

        return copy.deepcopy(
            element
        )

    except Exception:

        try:

            return element.clone()

        except Exception:

            return element


# ============================================================
# 建立 Note / Rest
# ============================================================

def create_segment(
    original,
    duration
):

    duration = safe_duration(
        duration
    )

    if isinstance(
        original,
        m21note.Note
    ):

        new_element = clone_element(
            original
        )

        new_element.duration.quarterLength = duration

        return new_element

    if isinstance(
        original,
        m21note.Rest
    ):

        new_element = m21note.Rest()

        new_element.duration.quarterLength = duration

        return new_element

    # 其他元素不直接保留
    return None


# ============================================================
# Tie
# ============================================================

def apply_tie(
    element,
    tie_type
):

    if not isinstance(
        element,
        m21note.Note
    ):

        return

    try:

        element.tie = m21note.Tie(
            tie_type
        )

    except Exception:

        pass


# ============================================================
# 將一個元素切割成不跨小節的片段
# ============================================================

def split_element(
    element,
    start,
    duration
):

    segments = []

    start = quantize(
        start
    )

    duration = safe_duration(
        duration
    )

    end = quantize(
        start + duration
    )

    if end <= start:

        return segments

    current = start

    first = True

    while current < end - 1e-9:

        # ----------------------------------------------------
        # 目前位於哪個小節
        # ----------------------------------------------------

        measure_index = math.floor(
            current / MEASURE_LENGTH
        )

        measure_start = (
            measure_index
            * MEASURE_LENGTH
        )

        measure_end = (
            measure_start
            + MEASURE_LENGTH
        )

        # ----------------------------------------------------
        # 如果剛好位於小節線
        # ----------------------------------------------------

        if current >= measure_end - 1e-9:

            current = measure_end

            continue

        # ----------------------------------------------------
        # 本段最多只能到小節線
        # ----------------------------------------------------

        segment_end = min(
            end,
            measure_end
        )

        segment_duration = (
            segment_end
            - current
        )

        segment_duration = quantize(
            segment_duration
        )

        if segment_duration <= 0:

            current += QUANTUM

            continue

        new_element = create_segment(
            element,
            segment_duration
        )

        if new_element is None:

            break

        # ----------------------------------------------------
        # 跨小節 Note
        # ----------------------------------------------------

        crosses_barline = (
            segment_end < end - 1e-9
        )

        if isinstance(
            new_element,
            m21note.Note
        ):

            if crosses_barline:

                if first:

                    apply_tie(
                        new_element,
                        "start"
                    )

                else:

                    apply_tie(
                        new_element,
                        "continue"
                    )

            else:

                if not first:

                    apply_tie(
                        new_element,
                        "stop"
                    )

        segments.append(
            (
                current,
                new_element
            )
        )

        current = segment_end

        first = False

    return segments


# ============================================================
# 收集 MIDI
# ============================================================

def collect_elements(
    original_part
):

    raw = []

    elements = list(
        original_part.recurse().notesAndRests
    )

    print(
        f"原始 Note/Rest 數量："
        f"{len(elements)}"
    )

    for element in elements:

        try:

            start = get_absolute_offset(
                element,
                original_part
            )

        except Exception:

            continue

        try:

            duration = float(
                element.duration.quarterLength
            )

        except Exception:

            continue

        if duration <= 0:

            continue

        start = quantize(
            start
        )

        duration = safe_duration(
            duration
        )

        raw.append(
            (
                start,
                duration,
                element
            )
        )

    raw.sort(
        key=lambda x: x[0]
    )

    return raw


# ============================================================
# 建立安全 Part
# ============================================================

def build_safe_part(
    original_part,
    detected_key
):

    print(
        "處理 Part..."
    )

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
        clone_element(
            detected_key
        )
    )

    raw = collect_elements(
        original_part
    )

    output_count = 0
    split_count = 0

    # --------------------------------------------------------
    # 重新切割
    # --------------------------------------------------------

    for start, duration, element in raw:

        end = start + duration

        # ----------------------------------------------------
        # 判斷是否跨小節
        # ----------------------------------------------------

        start_measure = math.floor(
            start / MEASURE_LENGTH
        )

        end_measure = math.floor(
            max(
                start,
                end - 1e-9
            )
            / MEASURE_LENGTH
        )

        if start_measure != end_measure:

            split_count += 1

        pieces = split_element(
            element,
            start,
            duration
        )

        for piece_offset, piece in pieces:

            # ------------------------------------------------
            # 關鍵：
            #
            # piece_offset 是「絕對 offset」
            #
            # 不使用 append()
            # ------------------------------------------------

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
# 深度驗證
# ============================================================

def validate_no_cross_barline(
    score,
    verbose=True
):

    errors = []

    for part_index, part in enumerate(
        score.parts,
        start=1
    ):

        measures = part.getElementsByClass(
            stream.Measure
        )

        for measure in measures:

            measure_number = (
                measure.number
            )

            measure_duration = (
                float(
                    measure.duration.quarterLength
                )
                if measure.duration
                else MEASURE_LENGTH
            )

            if measure_duration <= 0:

                measure_duration = MEASURE_LENGTH

            for element in measure.notesAndRests:

                try:

                    offset = float(
                        element.offset
                    )

                    duration = float(
                        element.duration.quarterLength
                    )

                except Exception:

                    continue

                end = (
                    offset
                    + duration
                )

                # ------------------------------------------------
                # Measure 內 offset 是相對 offset
                #
                # 允許非常小的浮點誤差
                # ------------------------------------------------

                if end > measure_duration + 1e-6:

                    element_type = (
                        "NOTE"
                        if isinstance(
                            element,
                            m21note.Note
                        )
                        else "REST"
                    )

                    errors.append(
                        (
                            part_index,
                            measure_number,
                            element_type,
                            offset,
                            duration,
                            end
                        )
                    )

                    if verbose:

                        print(
                            f"❌ Part {part_index} "
                            f"Measure {measure_number} "
                            f"{element_type}: "
                            f"offset={offset:.4f} "
                            f"duration={duration:.4f} "
                            f"end={end:.4f}"
                        )

    if not errors:

        print(
            "✅ 深度驗證："
            "沒有跨小節音符"
        )

        return True

    print()

    print(
        f"❌ 發現跨小節元素："
        f"{len(errors)} 個"
    )

    return False


# ============================================================
# MusicXML 寫出後驗證
# ============================================================

def verify_written_musicxml(
    output_xml
):

    print()

    print(
        "重新讀取 MusicXML 驗證..."
    )

    try:

        verification_score = converter.parse(
            output_xml
        )

    except Exception as e:

        print(
            "❌ MusicXML 重新讀取失敗:",
            e
        )

        return False

    return validate_no_cross_barline(
        verification_score,
        verbose=True
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
        "Professional MVP 3.0"
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
    # 檢查
    # --------------------------------------------------------

    if not os.path.isfile(
        input_midi
    ):

        raise FileNotFoundError(
            f"找不到 MIDI: {input_midi}"
        )

    output_dir = os.path.dirname(
        output_xml
    )

    if output_dir:

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
    # 建立新的 Score
    # --------------------------------------------------------

    new_score = stream.Score()

    # --------------------------------------------------------
    # Part
    # --------------------------------------------------------

    for index, original_part in enumerate(
        score.parts
    ):

        print(
            f"處理 Part {index + 1}..."
        )

        new_part = build_safe_part(
            original_part,
            detected_key
        )

        new_score.insert(
            0,
            new_part
        )

    # --------------------------------------------------------
    # 重要：
    #
    # 這裡不直接使用 makeMeasures()
    #
    # 先建立 measures
    # --------------------------------------------------------

    print(
        "建立 4/4 小節..."
    )

    try:

        measured_score = new_score.makeMeasures(
            inPlace=False
        )

    except Exception as e:

        raise RuntimeError(
            f"建立 4/4 小節失敗: {e}"
        )

    # --------------------------------------------------------
    # 前置驗證
    # --------------------------------------------------------

    print()

    print(
        "檢查 MusicXML 前置結構..."
    )

    if not validate_no_cross_barline(
        measured_score,
        verbose=True
    ):

        raise RuntimeError(
            "MusicXML 前置結構仍存在跨小節元素"
        )

    # --------------------------------------------------------
    # 寫出 MusicXML
    # --------------------------------------------------------

    print(
        "寫入 MusicXML..."
    )

    measured_score.write(
        "musicxml",
        fp=output_xml
    )

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
    # 最重要：
    # 寫出後重新讀取
    # --------------------------------------------------------

    if not verify_written_musicxml(
        output_xml
    ):

        raise RuntimeError(
            "MusicXML 寫出後仍存在跨小節元素"
        )

    print()

    print(
        "========================================"
    )

    print(
        "🎉 MIDI -> MusicXML 成功"
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
        if len(sys.argv) >= 4
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