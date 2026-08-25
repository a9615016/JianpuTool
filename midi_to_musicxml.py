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

def build_part(original_part, detected_key):

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
    # 收集原 MIDI 音符
    # --------------------------------------------------------

    notes = list(
        original_part.recurse().notesAndRests
    )

    if not notes:

        return p

    # --------------------------------------------------------
    # 重要：
    #
    # 不使用 p.append(n)
    #
    # 因為 append() 會破壞原本 offset。
    #
    # 改用 insert(offset, element)
    # 保留 MIDI 原始時間位置。
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

    return p


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
    # 重新建立小節
    # --------------------------------------------------------

    print(
        "建立 4/4 小節..."
    )

    new_score = new_score.makeMeasures(
        inPlace=False
    )

    # --------------------------------------------------------
    # 對跨小節音符進行切割
    # --------------------------------------------------------

    print(
        "整理跨小節音符..."
    )

    try:

        new_score = new_score.sliceByQuarterLengths(
            quarterLengthList=[
                4.0
            ],
            addTies=True
        )

    except Exception as e:

        print(
            "⚠ sliceByQuarterLengths "
            "未執行:",
            e
        )

    # --------------------------------------------------------
    # 再次建立小節
    # --------------------------------------------------------

    new_score = new_score.makeMeasures(
        inPlace=False
    )

    # --------------------------------------------------------
    # 移除不必要的元素
    # --------------------------------------------------------

    for part in new_score.parts:

        # 確保每個 Part 有 4/4
        existing_ts = part.recurse().getElementsByClass(
            meter.TimeSignature
        )

        if not existing_ts:

            part.insert(
                0,
                meter.TimeSignature("4/4")
            )

        # 確保有調性
        existing_keys = part.recurse().getElementsByClass(
            m21key.Key
        )

        if not existing_keys:

            part.insert(
                0,
                detected_key
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