import sys
import os
import music21


print("CLEAN MUSICXML V2")


src = sys.argv[1]
dst = sys.argv[2]


print("input:")
print(src)

print("output:")
print(dst)


score = music21.converter.parse(src)


# ======================
# 移除 chord
# ======================

for part in score.parts:

    for c in list(part.recurse().getElementsByClass("Chord")):

        n = music21.note.Note(
            c.pitches[0]
        )

        n.duration = c.duration

        c.activeSite.replace(
            c,
            n
        )



# ======================
# 強制單聲部
# ======================

for part in score.parts:

    part.removeByClass("Voice")



# ======================
# Quantize
# ======================

print("quantize")

score.quantize(
    quarterLengthDivisors=[
        16,
        8,
        4,
        2,
        1
    ],
    processOffsets=True,
    processDurations=True
)



# ======================
# 強制4/4
# ======================

for part in score.parts:

    for m in part.getElementsByClass(
        music21.stream.Measure
    ):

        m.timeSignature = music21.meter.TimeSignature(
            "4/4"
        )



# ======================
# 重新切小節
# ======================

print("make measures")

for part in score.parts:

    part.makeMeasures(
        inPlace=True
    )



# ======================
# 修正最後超長音
# ======================

for n in score.recurse().notes:

    if n.duration.quarterLength > 4:

        n.duration.quarterLength = 4



# ======================
# output
# ======================

score.write(
    "musicxml",
    fp=dst
)


print("完成:")
print(dst)

print(
    "SIZE:",
    os.path.getsize(dst)
)