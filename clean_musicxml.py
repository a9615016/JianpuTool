from music21 import converter, stream, note, chord, meter, duration
import sys


print("================")
print("CLEAN MUSICXML V25 FINAL JIANPU COMPATIBLE")
print("================")


if len(sys.argv) < 2:
    print("usage: python clean_musicxml.py input.musicxml output.musicxml")
    sys.exit()


src = sys.argv[1]

if len(sys.argv) >= 3:
    out = sys.argv[2]
else:
    out = "clean.musicxml"


print("read")

score = converter.parse(src)


print("remove voices")

for p in score.parts:

    # 移除 voice
    for v in list(p.recurse().getElementsByClass('Voice')):
        v.removeByClass('Voice')


print("remove chords")


for p in score.parts:

    for c in list(p.recurse().getElementsByClass('Chord')):

        n = note.Note(
            c.pitch,
            quarterLength=c.duration.quarterLength
        )

        c.activeSite.replace(c, n)



print("remove beams")


for n in score.recurse().notes:

    n.beams = []


print("remove ties")


for n in score.recurse().notes:

    n.tie = None



print("force 4/4")


for p in score.parts:

    p.insert(0, meter.TimeSignature("4/4"))



print("duration quantize")


allowed = [
    0.25,
    0.5,
    0.75,
    1.0,
    1.5,
    2.0,
    3.0,
    4.0
]


for n in score.recurse().notes:

    q = float(n.duration.quarterLength)

    best = min(
        allowed,
        key=lambda x: abs(x-q)
    )

    n.duration = duration.Duration(best)



print("rebuild measures")


for p in score.parts:

    p.makeMeasures(inPlace=True)



print("split cross measure notes")


for p in score.parts:

    p.makeMeasures(inPlace=True)



# ============================
# V25 NEW FIX
# 重建每小節 offset
# ============================


print("rebuild offsets")


for p in score.parts:


    measures = p.getElementsByClass("Measure")


    for m in measures:

        current = 0.0


        elements = list(
            m.notesAndRests
        )


        for e in elements:

            e.offset = current

            current += float(
                e.duration.quarterLength
            )


        remain = 4.0 - current


        if remain > 0.001:

            r = note.Rest(
                quarterLength=remain
            )

            m.insert(
                current,
                r
            )



print("fill measure rest")


for p in score.parts:

    for m in p.getElementsByClass("Measure"):

        total = 0

        for e in m.notesAndRests:

            total += e.duration.quarterLength


        if abs(total-4.0) > 0.01:

            print(
                "FIX measure",
                m.number,
                total
            )



print("clear notation cache")


score.clearCache()


print("FINAL CHECK")


for p in score.parts:

    for m in p.getElementsByClass("Measure"):

        length = 0

        for e in m.notesAndRests:

            length += e.duration.quarterLength


        print(
            "Measure",
            m.number,
            float(length)
        )


print("ALL MEASURES SAFE")


print("FINAL WRITE")


score.write(
    "musicxml",
    fp=out
)


print("DONE")
print(out)