import sys
from music21 import converter, stream, note, chord, meter, duration
from fractions import Fraction


print("==============================")
print("CLEAN MUSICXML V27")
print("JIANPU_LY COMPATIBLE")
print("==============================")


if len(sys.argv) < 3:
    print(
        "usage: python clean_musicxml.py input.musicxml output.musicxml"
    )
    sys.exit()


input_file = sys.argv[1]
output_file = sys.argv[2]


print("READ")
score = converter.parse(input_file)



# ==========================
# duration quantize
# ==========================

allowed = [
    Fraction(1,16),
    Fraction(1,8),
    Fraction(3,16),
    Fraction(1,4),
    Fraction(3,8),
    Fraction(1,2),
    Fraction(3,4),
    Fraction(1),
    Fraction(2),
    Fraction(3),
    Fraction(4)
]


def snap_duration(value):

    f = Fraction(value).limit_denominator(96)

    return float(
        min(
            allowed,
            key=lambda x: abs(x-f)
        )
    )



print("REMOVE VOICE")

for p in score.parts:

    # force 4/4

    p.insert(
        0,
        meter.TimeSignature("4/4")
    )


    notes=[]


    for el in p.recurse():

        if isinstance(el, chord.Chord):

            # keep highest note only
            n = note.Note(
                el.highest.pitch
            )

            n.duration.quarterLength = (
                el.duration.quarterLength
            )

            notes.append(n)


        elif isinstance(el,note.Note):

            notes.append(el)


    p.removeByClass(
        'Voice'
    )



    print("QUANTIZE")

    for n in notes:

        n.duration.quarterLength = (
            snap_duration(
                n.duration.quarterLength
            )
        )


        # remove tie

        n.tie = None



# ==========================
# rebuild measures
# ==========================


print("REBUILD MEASURES")


new_score = stream.Score()


for p in score.parts:


    new_part = stream.Part()


    new_part.insert(
        0,
        meter.TimeSignature("4/4")
    )


    current = 0


    for n in p.flat.notes:

        q = n.duration.quarterLength


        # prevent crossing bar

        remain = 4 - (current % 4)


        if q > remain:

            n.duration.quarterLength = remain


        new_part.append(n)


        current += n.duration.quarterLength



    # fill last measure

    remain = 4 - (current % 4)

    if remain != 4:

        r = note.Rest()

        r.duration.quarterLength = remain

        new_part.append(r)



    new_score.append(new_part)



# ==========================
# check
# ==========================


print("FINAL CHECK")


for i,m in enumerate(
    new_score.parts[0].getElementsByClass("Measure"),
    1
):

    total = sum(
        x.duration.quarterLength
        for x in m.notesAndRests
    )

    print(
        "Measure",
        i,
        total
    )



# ==========================
# write
# ==========================


print("WRITE")

new_score.write(
    "musicxml",
    fp=output_file
)


print("DONE")
print(output_file)