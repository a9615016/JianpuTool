print("######## V91 LOADED ########")
from music21 import *
import sys


print("====================================")
print("CLEAN MUSICXML V91 LOADED")
print("NOTE STREAM REBUILD FOR JIANPU_LY")
print("====================================")


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
# collect notes
# =========================

print("COLLECT NOTE STREAM")


notes=[]


for n in score.recurse().notesAndRests:

    x=n

    x.duration.quarterLength = min(
        [
            0.25,
            0.5,
            0.75,
            1,
            1.5,
            2,
            3,
            4
        ],
        key=lambda a:
        abs(a-float(x.duration.quarterLength))
    )


    x.tie=None

    try:
        x.beams = beam.Beams()
    except:
        pass


    notes.append(x)



print(
    "TOTAL EVENTS:",
    len(notes)
)



# =========================
# create new score
# =========================

print("REBUILD SCORE")


new_score = stream.Score()

part = stream.Part()


part.insert(
    0,
    meter.TimeSignature("4/4")
)



measure_no=1

m=stream.Measure(
    number=measure_no
)


pos=0.0



for n in notes:


    length=float(
        n.duration.quarterLength
    )


    # ----------------------
    # split cross bar notes
    # ----------------------

    while length > 0:


        remain = 4-pos


        take=min(
            length,
            remain
        )


        if n.isRest:

            obj=note.Rest()

        else:

            obj=n.clone()



        obj.duration.quarterLength=take


        m.append(obj)


        pos += take
        length -= take



        # next measure

        if abs(pos-4)<0.001:


            # fill safety

            total=sum(
                float(x.duration.quarterLength)
                for x in m.notesAndRests
            )


            if total < 4:

                r=note.Rest()

                r.duration.quarterLength=4-total

                m.append(r)



            part.append(m)


            measure_no+=1


            m=stream.Measure(
                number=measure_no
            )


            pos=0.0



# =========================
# final rest
# =========================

if pos>0:


    r=note.Rest()

    r.duration.quarterLength=4-pos

    m.append(r)


    part.append(m)



new_score.append(part)



# =========================
# FINAL CHECK
# =========================

print("====================")
print("FINAL CHECK V91")
print("====================")


bad=False


for m in part.getElementsByClass(
    stream.Measure
):


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

        bad=True



if bad:

    print(
        "WARNING measure mismatch"
    )

else:

    print(
        "ALL MEASURE 4.0 OK"
    )



# =========================
# write
# =========================

print("WRITE MUSICXML")


new_score.write(
    "musicxml",
    fp=dst
)


print("DONE")
print(dst)