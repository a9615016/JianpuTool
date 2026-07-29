from music21 import *
import sys


print("################################")
print("CLEAN MUSICXML V90 LOADED")
print("JIANPU_LY STRICT 4/4 MODE")
print("################################")


if len(sys.argv) < 3:
    print(
        "usage: python clean_musicxml.py input.musicxml output.musicxml"
    )
    sys.exit(1)


src = sys.argv[1]
dst = sys.argv[2]


print("READ")

score = converter.parse(src)



# ==========================
# remove voices
# ==========================

print("remove voices")

for n in score.recurse().notes:

    try:
        n.voice = None
    except:
        pass



# ==========================
# remove chords
# ==========================

print("remove chords")

for c in list(
    score.recurse().getElementsByClass(chord.Chord)
):

    if len(c.notes):

        n = c.notes[0]

        n.duration = c.duration

        c.activeSite.replace(c,n)



# ==========================
# remove beams
# ==========================

print("remove beams")

for n in score.recurse().notes:

    n.beams = beam.Beams()



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

    part.insert(
        0,
        meter.TimeSignature("4/4")
    )



# ==========================
# quantize duration
# ==========================

print("duration quantize")


allowed = [
    0.25,
    0.5,
    0.75,
    1,
    1.5,
    2,
    3,
    4
]


def qduration(x):

    return min(
        allowed,
        key=lambda a:abs(a-x)
    )


for n in score.recurse().notesAndRests:

    n.duration.quarterLength = qduration(
        float(n.duration.quarterLength)
    )



# ==========================
# rebuild measures
# ==========================

print("rebuild measures")


for p in score.parts:

    p.makeMeasures(inPlace=True)



# ==========================
# JIANPU STRICT BAR FIX
# ==========================

print("JIANPU STRICT NORMALIZE")


for part in score.parts:


    measures = list(
        part.getElementsByClass(stream.Measure)
    )


    for m in measures:


        total = float(
            m.duration.quarterLength
        )


        print(
            "Before",
            m.number,
            total
        )


        # ------------------
        # trim > 4
        # ------------------

        if total > 4:


            print(
                "TRIM",
                m.number
            )


            remain = 4.0


            for n in list(
                m.notesAndRests
            ):

                length = float(
                    n.duration.quarterLength
                )


                if remain <= 0:

                    m.remove(n)


                elif length <= remain:

                    remain -= length


                else:

                    n.duration.quarterLength = remain
                    remain = 0



        # ------------------
        # fill < 4
        # ------------------

        total = float(
            m.duration.quarterLength
        )


        if total < 4:


            r = note.Rest()

            r.duration.quarterLength = (
                4-total
            )

            print(
                "REST",
                m.number,
                r.duration.quarterLength
            )


            m.append(r)



# ==========================
# rebuild again
# ==========================

print("FINAL REBUILD")


for p in score.parts:

    p.makeMeasures(inPlace=True)



# ==========================
# FINAL CHECK
# ==========================

print("================")
print("FINAL CHECK")
print("================")


bad=False


for m in score.parts[0].getElementsByClass(
    stream.Measure
):

    total=float(
        m.duration.quarterLength
    )


    print(
        "Measure",
        m.number,
        total
    )


    if abs(total-4.0)>0.01:

        bad=True



if bad:

    print(
        "WARNING measure mismatch"
    )

else:

    print(
        "ALL MEASURE 4.0 OK"
    )



print("WRITE")


score.write(
    "musicxml",
    fp=dst
)


print("DONE")
print(dst)