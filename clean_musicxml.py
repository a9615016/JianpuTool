from music21 import *
import sys


print("==============================")
print("CLEAN MUSICXML V90")
print("JIANPU_LY STRICT 4/4 MODE")
print("==============================")


if len(sys.argv) < 3:
    print(
        "usage: python clean_musicxml.py input.musicxml output.musicxml"
    )
    sys.exit(1)


src = sys.argv[1]
dst = sys.argv[2]


print("READ")

score = converter.parse(src)



# =========================
# remove voices
# =========================

print("remove voices")

for n in score.recurse().notes:

    try:
        n.voice = None
    except:
        pass



# =========================
# remove chords
# =========================

print("remove chords")

for c in list(score.recurse().getElementsByClass(chord.Chord)):

    if len(c.notes) > 0:

        n = c.notes[0]

        n.duration = c.duration

        c.activeSite.replace(c, n)



# =========================
# remove beams
# =========================

print("remove beams")

for n in score.recurse().notes:

    n.beams = beam.Beams()



# =========================
# remove ties
# =========================

print("remove ties")

for n in score.recurse().notes:

    n.tie = None



# =========================
# force 4/4
# =========================

print("force 4/4")


for part in score.parts:

    for m in part.getElementsByClass(stream.Measure):

        m.timeSignature = meter.TimeSignature("4/4")



# =========================
# duration quantize
# =========================

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


def quantize(x):

    return min(
        allowed,
        key=lambda a: abs(a-x)
    )


for n in score.recurse().notesAndRests:

    q=float(
        n.duration.quarterLength
    )

    n.duration.quarterLength = quantize(q)



# =========================
# rebuild measures
# =========================

print("rebuild measures")


for p in score.parts:

    p.makeMeasures(inPlace=True)



# =========================
# STRICT 4/4 NORMALIZE
# =========================


print("jianpu_ly strict normalize")


for part in score.parts:


    measures=list(
        part.getElementsByClass(stream.Measure)
    )


    for m in measures:


        total=float(
            m.duration.quarterLength
        )


        print(
            "Measure",
            m.number,
            total
        )



        # -----------------
        # trim overflow
        # -----------------

        if total > 4:


            print(
                "TRIM",
                m.number
            )


            remain=4.0


            for n in list(
                m.notesAndRests
            ):

                length=float(
                    n.duration.quarterLength
                )


                if remain <=0:

                    m.remove(n)


                elif length <= remain:

                    remain -= length


                else:

                    n.duration.quarterLength = remain
                    remain=0



        # -----------------
        # fill missing
        # -----------------

        total=float(
            m.duration.quarterLength
        )


        if total < 4:


            r=note.Rest()

            r.duration.quarterLength = (
                4-total
            )


            print(
                "FILL REST",
                m.number,
                r.duration.quarterLength
            )


            m.append(r)




# =========================
# rebuild final
# =========================

print("FINAL REBUILD")


for p in score.parts:

    p.makeMeasures(inPlace=True)



# =========================
# final check
# =========================


print("FINAL CHECK")


bad=False


for m in score.parts[0].getElementsByClass(
    stream.Measure
):

    length=float(
        m.duration.quarterLength
    )


    print(
        "Measure",
        m.number,
        length
    )


    if abs(length-4.0)>0.01:

        bad=True



if bad:

    print(
        "WARNING measure mismatch"
    )

else:

    print(
        "ALL MEASURES 4/4 OK"
    )



print("WRITE")


score.write(
    "musicxml",
    fp=dst
)


print("DONE")
print(dst)