import sys
import json
import os
import copy
import math

from music21 import converter, stream, meter, key as m21key
from music21 import note as m21note
from music21 import tie as m21tie


# ============================================================
# JianpuTool Professional MVP 3.0
#
# MIDI -> MusicXML Stable Version
#
# 核心：
# 1. 強制 4/4
# 2. 1/16 拍量化
# 3. Note 不跨小節
# 4. Rest 不跨小節
# 5. 跨小節 Note 自動切割 + Tie
# 6. 每小節補滿 4 拍
# 7. 避免 makeMeasures 破壞原始 offset
# 8. MusicXML 寫出後重新讀取
# 9. 修正最後一小節不足造成的 LilyPond warning
# ============================================================


TIME_SIGNATURE = "4/4"

MEASURE_LENGTH = 4.0

QUANTUM = 0.25

EPS = 1e-7


# ============================================================
# 調性
# ============================================================

def load_key(info_json):

    if not info_json:
        print("⚠ 未提供 info.json，使用 C major")
        return m21key.Key("C", "major")

    if not os.path.isfile(info_json):
        print("⚠ 找不到 info.json，使用 C major")
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
            f"⚠ info.json 讀取失敗：{e}"
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

    if not tonic:
        tonic = "C"

    if not mode:
        mode = "major"

    print(
        f"✓ 調性：{tonic} {mode}"
    )

    try:

        return m21key.Key(
            tonic,
            mode
        )

    except Exception as e:

        print(
            f"⚠ 調性解析失敗：{e}"
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

    result = round(
        value / QUANTUM
    ) * QUANTUM

    # 避免 -0.0
    if abs(result) < EPS:
        result = 0.0

    return result


# ============================================================
# 安全長度
# ============================================================

def safe_duration(value):

    value = quantize(value)

    if value < QUANTUM:
        value = QUANTUM

    return value


# ============================================================
# 深拷貝
# ============================================================

def clone_element(element):

    try:
        return copy.deepcopy(element)

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

    # ------------------------------
    # Note
    # ------------------------------

    if isinstance(
        original,
        m21note.Note
    ):

        new_note = clone_element(
            original
        )

        new_note.duration.quarterLength = (
            duration
        )

        return new_note

    # ------------------------------
    # Rest
    # ------------------------------

    if isinstance(
        original,
        m21note.Rest
    ):

        new_rest = m21note.Rest()

        new_rest.duration.quarterLength = (
            duration
        )

        return new_rest

    return None


# ============================================================
# 設定 Tie
# ============================================================

def set_tie(
    element,
    tie_type
):

    if not isinstance(
        element,
        m21note.Note
    ):
        return

    try:

        element.tie = m21tie.Tie(
            tie_type
        )

    except Exception:

        pass


# ============================================================
# 切割跨小節元素
# ============================================================

def split_element(
    element,
    start,
    duration
):

    result = []

    start = quantize(start)

    duration = safe_duration(
        duration
    )

    end = quantize(
        start + duration
    )

    if end <= start + EPS:
        return result

    current = start

    first_segment = True

    while current < end - EPS:

        # ------------------------------
        # 找目前所在小節
        # ------------------------------

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

        # 防止浮點誤差
        if current < measure_start:
            current = measure_start

        # ------------------------------
        # 本段不能超過小節線
        # ------------------------------

        segment_end = min(
            end,
            measure_end
        )

        segment_duration = (
            segment_end - current
        )

        segment_duration = quantize(
            segment_duration
        )

        if segment_duration <= EPS:

            current = measure_end

            continue

        piece = create_segment(
            element,
            segment_duration
        )

        if piece is None:
            break

        # ------------------------------
        # 判斷是否跨小節
        # ------------------------------

        crosses_forward = (
            segment_end < end - EPS
        )

        if isinstance(
            piece,
            m21note.Note
        ):

            if first_segment:

                if crosses_forward:
                    set_tie(
                        piece,
                        "start"
                    )

            else:

                if crosses_forward:
                    set_tie(
                        piece,
                        "continue"
                    )

                else:
                    set_tie(
                        piece,
                        "stop"
                    )

        result.append(
            (
                current,
                piece
            )
        )

        current = segment_end

        first_segment = False

    return result


# ============================================================
# 取得絕對 offset
# ============================================================

def absolute_offset(
    element,
    part
):

    try:

        return float(
            element.getOffsetInHierarchy(
                part
            )
        )

    except Exception:

        try:
            return float(
                element.offset
            )

        except Exception:

            return 0.0


# ============================================================
# 收集 MIDI Note / Rest
# ============================================================

def collect_elements(
    original_part
):

    elements = list(
        original_part.recurse().notesAndRests
    )

    print(
        f"原始 Note/Rest：{len(elements)}"
    )

    result = []

    for element in elements:

        try:

            start = absolute_offset(
                element,
                original_part
            )

            duration = float(
                element.duration.quarterLength
            )

        except Exception:

            continue

        if duration <= EPS:
            continue

        start = quantize(
            start
        )

        duration = safe_duration(
            duration
        )

        result.append(
            (
                start,
                duration,
                element
            )
        )

    result.sort(
        key=lambda x: (
            x[0],
            x[2].__class__.__name__
        )
    )

    return result


# ============================================================
# 建立安全 Part
# ============================================================

def build_safe_part(
    original_part,
    detected_key
):

    print(
        "建立安全 Part..."
    )

    part = stream.Part()

    # ------------------------------
    # 4/4
    # ------------------------------

    part.insert(
        0,
        meter.TimeSignature(
            TIME_SIGNATURE
        )
    )

    # ------------------------------
    # 調性
    # ------------------------------

    part.insert(
        0,
        clone_element(
            detected_key
        )
    )

    raw = collect_elements(
        original_part
    )

    split_count = 0

    output_count = 0

    max_end = 0.0

    # ------------------------------
    # 找歌曲總長度
    # ------------------------------

    for start, duration, element in raw:

        end = (
            start + duration
        )

        if end > max_end:
            max_end = end

    max_end = quantize(
        max_end
    )

    print(
        f"量化後歌曲長度："
        f"{max_end:.2f} 拍"
    )

    # ------------------------------
    # 切割所有元素
    # ------------------------------

    for start, duration, element in raw:

        end = start + duration

        start_measure = math.floor(
            start / MEASURE_LENGTH
        )

        end_measure = math.floor(
            max(
                start,
                end - EPS
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

        for offset, piece in pieces:

            part.insert(
                offset,
                piece
            )

            output_count += 1

    # ------------------------------
    # 最後補到完整小節
    # ------------------------------

    if max_end > 0:

        final_measure_end = (
            math.ceil(
                max_end / MEASURE_LENGTH
            )
            * MEASURE_LENGTH
        )

        if (
            final_measure_end
            > max_end + EPS
        ):

            rest_length = (
                final_measure_end
                - max_end
            )

            rest_length = quantize(
                rest_length
            )

            if rest_length >= QUANTUM:

                rest = m21note.Rest()

                rest.duration.quarterLength = (
                    rest_length
                )

                part.insert(
                    max_end,
                    rest
                )

                print(
                    f"✓ 最後補休止符："
                    f"{rest_length:.2f} 拍"
                )

    print(
        f"輸出 Note/Rest："
        f"{output_count}"
    )

    print(
        f"跨小節切割："
        f"{split_count}"
    )

    return part


# ============================================================
# 建立 Measure
# ============================================================

def make_measures_safe(
    score
):

    print(
        "建立 4/4 小節..."
    )

    try:

        measured = score.makeMeasures(
            inPlace=False
        )

    except Exception as e:

        raise RuntimeError(
            f"建立小節失敗：{e}"
        )

    return measured


# ============================================================
# 小節完整性檢查
# ============================================================

def validate_measures(
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

            expected = MEASURE_LENGTH

            try:

                duration = float(
                    measure.duration.quarterLength
                )

            except Exception:

                duration = 0.0

            # 最後一小節如果不是完整小節，
            # 後面會由補休止符修正。
            #
            # 這裡主要檢查「元素不可超出小節」。

            for element in measure.notesAndRests:

                try:

                    offset = float(
                        element.offset
                    )

                    length = float(
                        element.duration.quarterLength
                    )

                except Exception:

                    continue

                end = offset + length

                if end > expected + EPS:

                    info = (
                        part_index,
                        measure.number,
                        type(element).__name__,
                        offset,
                        length,
                        end
                    )

                    errors.append(
                        info
                    )

                    if verbose:

                        print(
                            f"❌ Part {part_index} "
                            f"小節 {measure.number} "
                            f"{type(element).__name__} "
                            f"offset={offset:.3f} "
                            f"duration={length:.3f} "
                            f"end={end:.3f}"
                        )

    if errors:

        print()
        print(
            f"❌ 跨小節元素："
            f"{len(errors)}"
        )

        return False

    print(
        "✅ 深度驗證："
        "沒有跨小節元素"
    )

    return True


# ============================================================
# 檢查小節長度
# ============================================================

def report_measure_lengths(
    score
):

    print()
    print(
        "小節長度檢查..."
    )

    bad = []

    for part_index, part in enumerate(
        score.parts,
        start=1
    ):

        measures = part.getElementsByClass(
            stream.Measure
        )

        for measure in measures:

            try:

                length = float(
                    measure.duration.quarterLength
                )

            except Exception:

                continue

            # 允許最後空白小節
            if (
                abs(length - MEASURE_LENGTH)
                > EPS
            ):

                bad.append(
                    (
                        part_index,
                        measure.number,
                        length
                    )
                )

    if not bad:

        print(
            "✅ 所有小節均為 4/4"
        )

        return True

    print(
        f"⚠ 發現 {len(bad)} 個非 4 拍小節"
    )

    for item in bad[:20]:

        print(
            f"  Part={item[0]} "
            f"Measure={item[1]} "
            f"Length={item[2]:.3f}"
        )

    if len(bad) > 20:

        print(
            f"  ...其餘 {len(bad) - 20} 個略過"
        )

    return False


# ============================================================
# 寫出 MusicXML
# ============================================================

def write_musicxml(
    score,
    output_xml
):

    print(
        "寫入 MusicXML..."
    )

    try:

        score.write(
            "musicxml",
            fp=output_xml
        )

    except Exception as e:

        raise RuntimeError(
            f"MusicXML 寫出失敗：{e}"
        )

    if not os.path.isfile(
        output_xml
    ):

        raise RuntimeError(
            "MusicXML 檔案不存在"
        )

    size = os.path.getsize(
        output_xml
    )

    print(
        f"✓ MusicXML 完成："
        f"{size:,} bytes"
    )


# ============================================================
# 寫出後重新驗證
# ============================================================

def verify_written_musicxml(
    output_xml
):

    print()
    print(
        "重新讀取 MusicXML..."
    )

    try:

        score = converter.parse(
            output_xml
        )

    except Exception as e:

        print(
            f"❌ MusicXML 重新讀取失敗：{e}"
        )

        return False

    print(
        f"✓ 重新讀取成功"
        f" Parts={len(score.parts)}"
    )

    # ------------------------------
    # 跨小節檢查
    # ------------------------------

    if not validate_measures(
        score,
        verbose=True
    ):

        return False

    print(
        "✓ MusicXML 結構驗證完成"
    )

    return True


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
        "Professional MVP 3.0 Stable"
    )
    print(
        "========================================"
    )

    print(
        f"輸入 MIDI：{input_midi}"
    )

    print(
        f"輸出 XML：{output_xml}"
    )

    # ========================================================
    # 檔案檢查
    # ========================================================

    if not os.path.isfile(
        input_midi
    ):

        raise FileNotFoundError(
            f"找不到 MIDI：{input_midi}"
        )

    output_dir = os.path.dirname(
        os.path.abspath(
            output_xml
        )
    )

    os.makedirs(
        output_dir,
        exist_ok=True
    )

    # ========================================================
    # 讀取 MIDI
    # ========================================================

    print()
    print(
        "[1/6] 讀取 MIDI..."
    )

    try:

        original_score = converter.parse(
            input_midi
        )

    except Exception as e:

        raise RuntimeError(
            f"MIDI 讀取失敗：{e}"
        )

    print(
        f"✓ Parts："
        f"{len(original_score.parts)}"
    )

    if len(original_score.parts) == 0:

        raise RuntimeError(
            "MIDI 沒有可處理的 Part"
        )

    # ========================================================
    # 調性
    # ========================================================

    print()
    print(
        "[2/6] 載入調性..."
    )

    detected_key = load_key(
        info_json
    )

    # ========================================================
    # 建立新的 Score
    # ========================================================

    print()
    print(
        "[3/6] 建立安全 MusicXML 結構..."
    )

    new_score = stream.Score()

    # --------------------------------------------------------
    # metadata
    # --------------------------------------------------------

    try:

        new_score.metadata = copy.deepcopy(
            original_score.metadata
        )

    except Exception:

        pass

    # --------------------------------------------------------
    # 每個 Part
    # --------------------------------------------------------

    for index, original_part in enumerate(
        original_score.parts
    ):

        print()
        print(
            f"--- Part {index + 1} ---"
        )

        new_part = build_safe_part(
            original_part,
            detected_key
        )

        new_score.insert(
            0,
            new_part
        )

    # ========================================================
    # 建立小節
    # ========================================================

    print()
    print(
        "[4/6] 建立 4/4 小節..."
    )

    measured_score = make_measures_safe(
        new_score
    )

    # ========================================================
    # 前置驗證
    # ========================================================

    print()
    print(
        "[5/6] MusicXML 前置驗證..."
    )

    if not validate_measures(
        measured_score,
        verbose=True
    ):

        raise RuntimeError(
            "前置驗證失敗：存在跨小節元素"
        )

    report_measure_lengths(
        measured_score
    )

    # ========================================================
    # 寫出
    # ========================================================

    write_musicxml(
        measured_score,
        output_xml
    )

    # ========================================================
    # 寫出後驗證
    # ========================================================

    print()
    print(
        "[6/6] 寫出後重新驗證..."
    )

    if not verify_written_musicxml(
        output_xml
    ):

        raise RuntimeError(
            "MusicXML 寫出後驗證失敗"
        )

    # ========================================================
    # 完成
    # ========================================================

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

    print(
        f"MusicXML：{output_xml}"
    )

    return output_xml


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":

    if len(sys.argv) < 3:

        print()
        print(
            "用法："
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