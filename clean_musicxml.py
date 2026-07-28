# clean_musicxml.py
# CLEAN MUSICXML V62
# OFFSET RESET ENGINE
# BasicPitch + Render + jianpu_ly

import sys
from music21 import converter, stream, note, chord, meter

print("================")
print("CLEAN MUSICXML V62 OFFSET RESET ENGINE")
print("================")


if len(sys.argv) < 2:
    print("usage: python clean_musicxml.py input.xml output.xml")
    sys.exit()


src = sys.argv[1]
out = sys.argv[2] if len(sys.argv) > 2 else "clean.musicxml"


print("read")

score = converter.parse(src)


# ------------------------
# remove voices
# ------------------------

print("remove voices")

for p in score.parts:
    for v in list(p.recurse().getElementsByClass('Voice')):
        try:
            v.activeSite.remove(v)
        except:
            pass


# ------------------------
# remove chords
# ------------------------

print("remove chords")

for c in list(score.recurse().getElementsByClass(chord.Chord)):

    if len(c.notes) > 0:

        n = note.Note(
            c.notes[0].pitch
        )

        n.duration.quarterLength = c.duration.quarterLength

        c.activeSite.replace(
            c,
            n
        )


# ------------------------
# remove notation
# ------------------------

print("remove beams")

for n in score.recurse().notes:

    try:
        n.beams = []
    except:
        pass


print("remove ties")

for n in score.recurse().notes:

    try:
        n.tie = None
    except:
        pass



# ------------------------
# 4/4
# ------------------------

print("force 4/4")

for p in score.parts:
    p.insert(
        0,
        meter.TimeSignature("4/4")
    )



# ------------------------
# quantize
# ------------------------

print("duration quantize")


def qgrid(x):

    # quarter grid
    return round(float(x) * 4) / 4



for n in score.recurse().notesAndRests:

    n.duration.quarterLength = qgrid(
        n.duration.quarterLength
    )

    try:
        n.offset = qgrid(n.offset)
    except:
        pass



# ------------------------
# rebuild measures
# ------------------------

print("rebuild measures")


for part in score.parts:


    old = list(
        part.getElementsByClass(stream.Measure)
    )


    if not old:
        continue


    new=[]


    measure_no=1


    current_measure = stream.Measure(
        number=measure_no
    )

    pos=0.0


    for m in old:


        for el in m.notesAndRests:


            dur=float(
                el.duration.quarterLength
            )

            dur=qgrid(dur)


            while dur > 0:


                remain = 4.0-pos


                take=min(
                    dur,
                    remain
                )


                new_el = el.clone()

                new_el.duration.quarterLength = take


                current_measure.insert(
                    pos,
                    new_el
                )


                pos += take
                dur -= take



                if pos >= 4.0-0.001:

                    new.append(
                        current_measure
                    )

                    measure_no += 1

                    current_measure = stream.Measure(
                        number=measure_no
                    )

                    pos=0.0



    if pos > 0:

        rest = note.Rest(
            quarterLength=4-pos
        )

        current_measure.insert(
            pos,
            rest
        )

        new.append(
            current_measure
        )



    part.remove(
        old
    )


    for m in new:
        part.append(m)



# ------------------------
# final check
# ------------------------

print("clear notation cache")


print("FINAL CHECK")

safe=True


for p in score.parts:

    for m in p.getElementsByClass(stream.Measure):

        length=float(
            m.duration.quarterLength
        )

        print(
            "Measure",
            m.number,
            length
        )


        if abs(length-4.0)>0.01:
            safe=False



if safe:
    print("ALL MEASURES SAFE")
else:
    print("WARNING measure mismatch")



print("FINAL WRITE")


score.write(
    "musicxml",
    fp=out
)


print("DONE")
print(out)