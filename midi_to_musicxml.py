import sys
import json
import os

from music21 import (
    converter,
    stream,
    meter,
    key as m21key,
)


# ============================================================
# MIDI -> MusicXML
# JianpuTool 穩定版
#
# 重點：
# 1. 保留 MIDI 原始 offset
# 2. 固定 4/4
# 3. 使用 makeTies() 處理跨小節音符
# 4. 寫出後重新讀取 MusicXML 驗證
# 5. 若仍有跨小節事件，直接停止
# ============================================================


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

    ts = meter.TimeSignature(
        "4/4"
    )

    p.insert(
        0,
        ts
    )

    # --------------------------------------------------------
    # 調性
    # --------------------------------------------------------

    p.insert(
        0,
        detected_key
    )

    # --------------------------------------------------------
    # 收集 MIDI Note / Rest
    # --------------------------------------------------------

    notes = list(
        original_part.recurse().notesAndRests
    )

    print(
        f"原始 Note/Rest 數量：{len(notes)}"
    )

    if not notes:

        return p

    output_count = 0

    # --------------------------------------------------------
    # 保留原始 offset
    # --------------------------------------------------------

    for element in notes:

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
        # 複製 element
        # ----------------------------------------------------

        try:

            element_copy = element.clone()

        except Exception:

            element_copy = element

        p.insert(
            offset,
            element_copy
        )

        output_count += 1

    print(
        f"輸出 Note/Rest 數量：{output_count}"
    )

    return p


# ============================================================
# 驗證是否存在跨小節事件
# ============================================================

def validate_no_cross_bar(
    part,
    label="MusicXML"
):

    errors = []

    measures = list(
        part.getElementsByClass(
            stream.Measure
        )
    )

    for measure in measures:

        measure_number = (
            measure.measureNumber
        )

        # ----------------------------------------------------
        # 目前 JianpuTool 固定 4/4
        # ----------------------------------------------------

        bar_length = 4.0

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
            # 跨越小節線
            # ------------------------------------------------

            if end > bar_length + 1e-8:

                if element.isRest:

                    kind = "REST"

                else:

                    kind = "NOTE"

                errors.append(
                    (
                        measure_number,
                        kind,
                        offset,
                        duration,
                        end
                    )
                )

    # --------------------------------------------------------
    # 發現錯誤
    # --------------------------------------------------------

    if errors:

        for (
            measure_number,
            kind,
            offset,
            duration,
            end
        ) in errors:

            print(
                f"❌ Part {label} "
                f"Measure {measure_number} "
                f"{kind}: "
                f"offset={offset:.4f} "
                f"duration={duration:.4f} "
                f"end={end:.4f}"
            )

        raise RuntimeError(
            "MusicXML 寫出後仍存在跨小節音符："
            f"{len(errors)} 個"
        )

    print(
        f"✅ {label} 深度驗證："
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

    # ========================================================
    # 檢查 MIDI
    # ========================================================

    if not os.path.isfile(
        input_midi
    ):

        raise FileNotFoundError(
            f"找不到 MIDI: {input_midi}"
        )

    # ========================================================
    # 讀取 MIDI
    # ========================================================

    print(
        "讀取 MIDI..."
    )

    score = converter.parse(
        input_midi
    )

    print(
        f"✓ Parts: {len(score.parts)}"
    )

    # ========================================================
    # 調性
    # ========================================================

    detected_key = load_key(
        info_json
    )

    # ========================================================
    # 建立新 Score
    # ========================================================

    new_score = stream.Score()

    # ========================================================
    # Part
    # ========================================================

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

    # ========================================================
    # 建立 4/4 小節
    # ========================================================

    print(
        "建立 4/4 小節..."
    )

    new_score = new_score.makeMeasures(
        inPlace=False
    )

    # ========================================================
    # 關鍵修正
    #
    # 使用 makeTies()
    #
    # 將跨小節 Note 切開
    # 並建立 tie。
    #
    # 也處理跨小節 Rest。
    # ========================================================

    print(
        "整理跨小節音符..."
    )

    try:

        new_score = new_score.makeTies(
            inPlace=False
        )

        print(
            "✓ makeTies 完成"
        )

    except Exception as e:

        print(
            "❌ makeTies 失敗:",
            e
        )

        raise RuntimeError(
            "makeTies 無法處理跨小節事件："
            f"{e}"
        )

    # ========================================================
    # 再次建立小節
    # ========================================================

    print(
        "重新建立 4/4 小節..."
    )

    new_score = new_score.makeMeasures(
        inPlace=False
    )

    # ========================================================
    # 確保拍號與調性
    # ========================================================

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
                meter.TimeSignature(
                    "4/4"
                )
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
                detected_key
            )

    # ========================================================
    # 寫入前檢查
    # ========================================================

    print()
    print(
        "檢查 MusicXML 前置結構..."
    )

    for index, part in enumerate(
        new_score.parts
    ):

        validate_no_cross_bar(
            part,
            f"Part {index + 1}"
        )

    # ========================================================
    # 儲存 MusicXML
    # ========================================================

    print(
        "寫入 MusicXML..."
    )

    new_score.write(
        "musicxml",
        fp=output_xml
    )

    # ========================================================
    # 確認檔案
    # ========================================================

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

    # ========================================================
    # 寫出後重新讀取
    # ========================================================

    print()
    print(
        "重新讀取 MusicXML 驗證..."
    )

    try:

        verify_score = converter.parse(
            output_xml
        )

    except Exception as e:

        raise RuntimeError(
            "MusicXML 寫出後無法重新讀取："
            f"{e}"
        )

    # ========================================================
    # 深度驗證
    # ========================================================

    for index, part in enumerate(
        verify_score.parts
    ):

        validate_no_cross_bar(
            part,
            f"Part {index + 1}"
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

        print(
            "============================================================"
        )

        sys.exit(1)