# final_quantize.py
# JianpuTool FINAL QUANTIZE
# MusicXML → 修正節拍 → 4/4 小節重建

from music21 import converter, stream, note, meter
import sys


if len(sys.argv) < 3:
    print(
        "Usage: python final_quantize.py input.musicxml output.musicxml"
    )
    sys.exit(1)



src = sys.argv[1]
dst = sys.argv[2]


print("Loading:", src)


score = converter.parse(src)



# ==========================
# 音符時間量化
# ==========================

allowed = [
    0.25,   # 16分
    0.5,    # 8分
    0.75,
    1.0,
    1.5,
    2.0,
    3.0,
    4.0
]


for part in score.parts:


    events = []


    for n in part.flatten().notesAndRests:


        length = float(n.quarterLength)


        best = min(
            allowed,
            key=lambda x: abs(x-length)
        )


        n.quarterLength = best


        events.append(n)



    # ==========================
    # 移除舊小節
    # ==========================

    part.removeByClass(
        stream.Measure
    )


    # ==========================
    # 強制 4/4
    # ==========================

    new_part = stream.Part()


    new_part.insert(
        0,
        meter.TimeSignature("4/4")
    )


    current = 0



    for n in events:


        dur = float(
            n.quarterLength
        )


        # 超過4拍
        if current + dur > 4:


            rest_len = 4-current


            if rest_len > 0:

                new_part.append(
                    note.Rest(
                        quarterLength=rest_len
                    )
                )


            current = 0



        new_part.append(n)


        current += dur



        # 一小節完成

        if abs(current-4) < 0.001:

            current = 0



    # 補最後不足

    if current > 0:


        new_part.append(
            note.Rest(
                quarterLength=4-current
            )
        )



    # 重新建立小節

    measures = new_part.makeMeasures()


    part.append(
        measures
    )



# ==========================
# 最後輸出
# ==========================

score.write(
    "musicxml",
    dst
)


print(
    "FINAL QUANTIZE OK:",
    dst
)