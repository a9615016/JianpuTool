print("========== USING V25 ==========")
print("================")
print("CLEAN MUSICXML V25 FINAL JIANPU COMPATIBLE")
print("================")

from music21 import converter, meter, note, chord, stream
import sys


INPUT = sys.argv[1]

if len(sys.argv) >= 3:
    OUTPUT = sys.argv[2]
else:
    OUTPUT = "clean.musicxml"


print("read")

score = converter.parse(INPUT)


print(
    "ORIGINAL NOTES",
    len(score.recurse().notes)
)


# ==========================
# remove chords
# ==========================

print("remove chords")

for c in list(score.recurse().getElementsByClass(chord.Chord)):

    n = note.Note(c.pitches[0])

    n.duration = c.duration

    c.activeSite.replace(c, n)



# ==========================
# remove voices
# ==========================

print("remove voices")

for v in score.recurse().voices:

    try:
        v.id = None
    except:
        pass



# ==========================
# remove beams
# ==========================

print("remove beams")

for n in score.recurse().notes:

    try:
        n.beams = []
    except:
        pass



# ==========================
# remove ties
# ==========================

print("remove ties")

for n in score.recurse().notes:

    n.tie = None



# ==========================
# force 4/4
# ==========================

print("force 4/4")


for part in score.parts:

    for m in part.getElementsByClass("Measure"):

        m.insert(
            0,
            meter.TimeSignature("4/4")
        )



# ==========================
# quantize
# ==========================

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


for n in score.recurse().notesAndRests:

    q = float(n.duration.quarterLength)

    nearest = min(
        allowed,
        key=lambda x:abs(x-q)
    )

    n.duration.clear()

    n.duration.quarterLength = nearest



# ==========================
# rebuild measures
# ==========================

print("rebuild measures")


for part in score.parts:

    part.makeMeasures(inPlace=True)



# ==========================
# repair measure overflow
# ==========================

print("repair measures")


for part in score.parts:

    for m in list(part.getElementsByClass("Measure")):


        total = sum(
            float(x.duration.quarterLength)
            for x in m.notesAndRests
        )


        while total > 4:


            diff = total - 4


            for n in reversed(
                list(m.notesAndRests)
            ):

                d = float(
                    n.duration.quarterLength
                )


                if d > diff:

                    n.duration.quarterLength = d-diff

                    break


            total = sum(
                float(x.duration.quarterLength)
                for x in m.notesAndRests
            )



# ==========================
# fill rest
# ==========================

print("fill measure rest")


for part in score.parts:

    for m in part.getElementsByClass("Measure"):


        total = sum(
            float(x.duration.quarterLength)
            for x in m.notesAndRests
        )


        if total < 4:

            r = note.Rest()

            r.duration.quarterLength = 4-total

            m.append(r)



# ==========================
# clear cache
# ==========================

print("clear notation cache")

score.stripTies()



# ==========================
# final check
# ==========================

print("FINAL CHECK")


ok=True


for part in score.parts:

    for m in part.getElementsByClass("Measure"):

        total=sum(
            float(x.duration.quarterLength)
            for x in m.notesAndRests
        )

        print(
            "Measure",
            m.number,
            total
        )


        if abs(total-4)>0.01:

            ok=False



if not ok:

    print(
        "WARNING measure mismatch"
    )

else:

    print(
        "ALL MEASURES OK"
    )



# ==========================
# write
# ==========================

print("FINAL WRITE")


score.write(
    "musicxml",
    fp=OUTPUT
)


print("DONE")

print(OUTPUT)