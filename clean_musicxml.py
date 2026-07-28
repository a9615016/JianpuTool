# ==========================================
# CLEAN MUSICXML V25
# FINAL JIANPU COMPATIBLE
# ==========================================

import sys
from music21 import converter, stream, note, chord, meter


print("================")
print("CLEAN MUSICXML V25 JIANPU FIX")
print("================")


if len(sys.argv) < 2:
    print(
        "usage: python clean_musicxml.py input.musicxml output.musicxml"
    )
    sys.exit()


INPUT = sys.argv[1]

if len(sys.argv) >= 3:
    OUTPUT = sys.argv[2]
else:
    OUTPUT = "clean.musicxml"


print("read")

score = converter.parse(INPUT)


# ------------------------------------------
# remove voices
# ------------------------------------------

print("remove voices")

for p in score.parts:

    for n in list(p.recurse().notesAndRests):

        if hasattr(n, "voice"):
            n.voice = None



# ------------------------------------------
# remove chords
# ------------------------------------------

print("remove chords")

for c in list(score.recurse().getElementsByClass(chord.Chord)):

    n = note.Note(
        c.pitches[0]
    )

    n.duration = c.duration

    c.activeSite.replace(
        c,
        n
    )



# ------------------------------------------
# remove beams
# ------------------------------------------

print("remove beams")

for n in score.recurse().notes:

    n.beams = []



# ------------------------------------------
# remove ties
# ------------------------------------------

print("remove ties")

for n in score.recurse().notes:

    n.tie = None



# ------------------------------------------
# force 4/4
# ------------------------------------------

print("force 4/4")


for p in score.parts:

    p.insert(
        0,
        meter.TimeSignature("4/4")
    )



# ------------------------------------------
# duration quantize
# ------------------------------------------

print("duration quantize")


allowed = [
    4,
    2,
    1,
    0.5,
    0.25
]


def quantize(x):

    return min(
        allowed,
        key=lambda a:abs(a-x)
    )



for n in score.recurse().notesAndRests:

    q = quantize(
        n.duration.quarterLength
    )

    n.duration.quarterLength = q



# ------------------------------------------
# rebuild measures
# ------------------------------------------

print("rebuild measures")


score.makeMeasures(
    inPlace=True
)



# ------------------------------------------
# fix every measure
# ------------------------------------------

print("fix measure")


for p in score.parts:


    for m in p.getElementsByClass(stream.Measure):


        # sort notes
        notes = list(
            m.notesAndRests
        )

        notes.sort(
            key=lambda x:x.offset
        )


        # remove bad offset
        current = 0


        for n in notes:

            if n.offset < current:

                n.offset = current


            current = (
                n.offset +
                n.duration.quarterLength
            )



        total = sum(
            x.duration.quarterLength
            for x in notes
        )


        # fill measure

        if total < 4:

            r = note.Rest()

            r.duration.quarterLength = (
                4-total
            )

            m.append(r)



print("rebuild measures")


score.makeMeasures(
    inPlace=True
)



# ------------------------------------------
# final check
# ------------------------------------------

print("clear notation cache")


for n in score.recurse().notes:

    n.tie = None
    n.beams = []



print("FINAL CHECK")


for m in score.parts[0].getElementsByClass(
    stream.Measure
):

    length = sum(
        n.duration.quarterLength
        for n in m.notesAndRests
    )

    print(
        "Measure",
        m.number,
        length
    )



print("FINAL WRITE")


score.write(
    "musicxml",
    fp=OUTPUT
)



print("DONE")
print(OUTPUT)