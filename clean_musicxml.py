# clean_musicxml.py
# CLEAN MUSICXML V62
# Offset Reset Engine
# BasicPitch + Render + jianpu_ly compatible

import sys
from music21 import converter, stream, note, chord, meter, bar

print("================")
print("CLEAN MUSICXML V62 OFFSET RESET ENGINE")
print("================")


if len(sys.argv) < 2:
    print("usage:")
    print("python clean_musicxml.py input.musicxml output.musicxml")
    sys.exit()


src = sys.argv[1]

if len(sys.argv) >= 3:
    out = sys.argv[2]
else:
    out = "clean.musicxml"


print("read")

score = converter.parse(src)


# -------------------------
# remove unwanted objects
# -------------------------

print("remove voices")
for p in score.parts:
    for v in p.recurse().getElementsByClass('Voice'):
        v.activeSite.remove(v)


print("remove chords")

for p in score.parts:
    for c in list(p.recurse().getElementsByClass('Chord')):
        n = c.notes[0]
        nn = note.Note(
            n.pitch,
            quarterLength=c.duration.quarterLength
        )
        c.activeSite.replace(c, nn)


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



# -------------------------
# force 4/4
# -------------------------

print("force 4/4")

for p in score.parts:
    p.insert(0, meter.TimeSignature("4/4"))



# -------------------------
# quantize duration
# -------------------------

print("duration quantize")


allowed = [
    4,
    2,
    1,
    0.5,
    0.25,
    0.125
]


def quantize(x):

    return min(
        allowed,
        key=lambda a:abs(a-x)
    )


for n in score.recurse().notes:

    q = quantize(
        float(n.duration.quarterLength)
    )

    n.duration.quarterLength = q



# -------------------------
# OFFSET RESET ENGINE
# -------------------------

print("offset reset")


for part in score.parts:

    measures = list(
        part.getElementsByClass(stream.Measure)
    )

    new_measures=[]


    for m in measures:

        nm = stream.Measure(
            number=m.number
        )

        current = 0.0


        for element in m.notesAndRests:

            dur=float(
                element.duration.quarterLength
            )


            # prevent overflow

            remain = 4.0-current


            if remain <= 0:
                break


            if dur > remain:

                # split note

                first = element.clone()
                first.duration.quarterLength = remain

                nm.insert(
                    current,
                    first
                )

                current += remain


                second = element.clone()
                second.duration.quarterLength = dur-remain

                new_measures.append(nm)

                nm = stream.Measure(
                    number=m.number+1
                )

                current=0

                nm.insert(
                    0,
                    second
                )

                current += second.duration.quarterLength

            else:

                nm.insert(
                    current,
                    element
                )

                current += dur



        # fill empty area

        if current < 4:

            r = note.Rest(
                quarterLength=4-current
            )

            nm.insert(
                current,
                r
            )


        new_measures.append(nm)



    part.remove(
        list(part.getElementsByClass(stream.Measure))
    )

    for nm in new_measures:
        part.append(nm)



# -------------------------
# FINAL CHECK
# -------------------------

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


        if abs(length-4)>0.01:
            safe=False



if safe:
    print("ALL MEASURES SAFE")
else:
    print("WARNING")


print("FINAL WRITE")


score.write(
    "musicxml",
    fp=out
)


print("DONE")
print(out)