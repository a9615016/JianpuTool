import sys
from music21 import converter, stream, meter

input_file = sys.argv[1]
output_file = sys.argv[2]


score = converter.parse(input_file)


# 強制 4/4
for part in score.parts:
    part.insert(
        0,
        meter.TimeSignature("4/4")
    )


# 重新切小節
new_score = stream.Score()

for part in score.parts:

    new_part = stream.Part()

    measures = part.makeMeasures(
        inPlace=False
    )

    for m in measures.getElementsByClass(
        'Measure'
    ):
        new_part.append(m)

    new_score.append(new_part)



# 關鍵：
# 讓 music21 自己重新計算 duration
new_score.makeNotation(
    inPlace=True
)


new_score.write(
    "musicxml",
    fp=output_file
)


print("bar split fix OK")