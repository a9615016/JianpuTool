from music21 import converter, stream, note, chord, meter
import sys
import os


print("==============================")
print("CLEAN MUSICXML V26 JIANPU FIX")
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
# remove bad notation
# ==========================

print("remove voices")
print("remove chords")
print("remove beams")
print("remove ties")


for part in score.parts:

    for el in list(part.recurse()):

        if isinstance(el, chord.Chord):

            n = note.Note(
                el.pitches[0]
            )

            n.duration = el.duration

            el.activeSite.replace(
                el,
                n
            )


        if isinstance(el, note.Note):

            el.tie = None



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
# duration quantize V26
# ==========================

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
        key=lambda y:abs(y-x)
    )



for n in score.recurse().notes:

    old = n.duration.quarterLength

    new = quantize(
        float(old)
    )

    n.duration.quarterLength = new



# ==========================
# rebuild measures
# ==========================

print("rebuild measures")


for part in score.parts:

    measures = part.makeMeasures()

    part.coreElementsChanged()



# ==========================
# final check
# ==========================


print("FINAL CHECK")


for m in score.parts[0].getElementsByClass(
    "Measure"
):

    length = float(
        m.duration.quarterLength
    )

    print(
        "Measure",
        m.number,
        length
    )



# ==========================
# write
# ==========================

print("FINAL WRITE")


score.write(
    "musicxml",
    fp=output_file
)


print("DONE")
print(output_file)