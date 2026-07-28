# ==========================================
# jianpu_fix_musicxml.py V2.0
# Jianpu_ly compatibility fixer
# ==========================================

import sys
from music21 import converter, stream, meter, note, chord
from music21.musicxml import m21ToXml


print("==========================")
print("JIANPU FIX MUSICXML V2.0")
print("==========================")


if len(sys.argv) < 3:
    print("usage:")
    print("python jianpu_fix_musicxml.py input.musicxml output.musicxml")
    sys.exit(1)


src = sys.argv[1]
dst = sys.argv[2]


print("READ")
score = converter.parse(src)


# -------------------------------
# remove voices/chords
# -------------------------------

print("remove voices chords")

for part in score.parts:

    for c in part.recurse().getElementsByClass(chord.Chord):
        n = c.notes[0]
        n.duration = c.duration
        c.activeSite.replace(c, n)


# -------------------------------
# remove notation
# -------------------------------

print("remove beams ties")

for n in score.recurse().notes:

    if hasattr(n, "beams"):
        n.beams = None

    if n.tie:
        n.tie = None



# -------------------------------
# force 4/4
# -------------------------------

print("force 4/4")


for part in score.parts:

    part.insert(
        0,
        meter.TimeSignature("4/4")
    )



# -------------------------------
# quantize duration
# -------------------------------

print("duration quantize")


allowed = [
    4.0,
    2.0,
    1.0,
    0.5,
    0.25
]


def quantize(x):

    best = min(
        allowed,
        key=lambda a: abs(a-x)
    )

    return best



for n in score.recurse().notesAndRests:

    q = quantize(
        float(n.duration.quarterLength)
    )

    n.duration.quarterLength = q



# -------------------------------
# rebuild measures
# -------------------------------

print("rebuild measures")


newScore = stream.Score()


for part in score.parts:

    newPart = stream.Part()

    current = 0

    measureNo = 1

    m = stream.Measure(number=measureNo)


    for el in part.recurse().notesAndRests:

        dur = el.duration.quarterLength


        # split crossing bar
        while current + dur > 4:

            remain = 4-current


            if isinstance(el, note.Note):

                a = note.Note(
                    el.pitch
                )
                a.duration.quarterLength = remain

            else:

                a = note.Rest()
                a.duration.quarterLength = remain


            m.append(a)

            dur -= remain


            current = 4


            newPart.append(m)


            measureNo += 1
            m = stream.Measure(
                number=measureNo
            )

            current = 0



        el.duration.quarterLength = dur

        m.append(el)

        current += dur



        if current == 4:

            newPart.append(m)

            measureNo += 1

            m = stream.Measure(
                number=measureNo
            )

            current = 0



    # fill rest


    if current < 4:

        r = note.Rest()

        r.duration.quarterLength = 4-current

        m.append(r)


    if len(m.notesAndRests)>0:

        newPart.append(m)


    newScore.append(newPart)



# -------------------------------
# final check
# -------------------------------


print("FINAL CHECK")


for p in newScore.parts:

    for m in p.getElementsByClass(
        stream.Measure
    ):

        total = sum(
            x.duration.quarterLength
            for x in m.notesAndRests
        )

        print(
            "Measure",
            m.number,
            total
        )


print("WRITE")


m21ToXml.GeneralObjectExporter(
    newScore
).parse()


newScore.write(
    "musicxml",
    fp=dst
)


print("DONE")
print(dst)