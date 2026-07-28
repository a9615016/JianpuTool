from music21 import converter, stream, meter, note, chord
import sys


print("==============================")
print("CLEAN MUSICXML V26.1 JIANPU FIX")
print("==============================")


if len(sys.argv) < 3:
    print("usage:")
    print("python clean_musicxml.py input.musicxml output.musicxml")
    sys.exit()


input_file = sys.argv[1]
output_file = sys.argv[2]


print("read")

score = converter.parse(input_file)



# ==========================
# remove chord
# ==========================

print("remove chords")


for part in score.parts:

    for c in list(
        part.recurse().getElementsByClass(chord.Chord)
    ):

        if len(c.pitches):

            n = note.Note(
                c.pitches[0]
            )

            n.duration = c.duration

            c.activeSite.replace(
                c,
                n
            )



# ==========================
# remove tie beam
# ==========================

print("remove beams")

for n in score.recurse().notes:

    n.beams = []


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
# quantize
# ==========================

print("duration quantize")


GRID = 0.25


for n in score.recurse().notesAndRests:

    value = float(
        n.duration.quarterLength
    )

    value = round(
        value / GRID
    ) * GRID


    if value <= 0:

        value = GRID


    n.duration.quarterLength = value



# ==========================
# rebuild measure
# ==========================

print("rebuild measures")


for part in score.parts:

    part.makeMeasures(
        inPlace=True
    )



# ==========================
# fill rest
# ==========================

print("fill measure rest")


for part in score.parts:


    for m in part.getElementsByClass(
        stream.Measure
    ):

        length = float(
            m.duration.quarterLength
        )


        if length < 4:

            m.append(
                note.Rest(
                    quarterLength=4-length
                )
            )



# ==========================
# FINAL NOTATION FIX
# ==========================

print("FINAL NOTATION FIX")


for part in score.parts:


    part.makeNotation(
        inPlace=True
    )


for n in score.recurse().notesAndRests:


    q = round(
        n.duration.quarterLength / 0.25
    ) * 0.25


    if q <= 0:

        q = 0.25


    n.duration.quarterLength = q



# ==========================
# final rebuild
# ==========================

print("final rebuild")


for part in score.parts:

    part.makeMeasures(
        inPlace=True
    )



# ==========================
# CHECK
# ==========================

print("FINAL CHECK")


bad = False


for m in score.parts[0].getElementsByClass(
    stream.Measure
):


    length = float(
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

    print("WARNING measure mismatch")

else:

    print("ALL MEASURES SAFE")



# ==========================
# WRITE
# ==========================

print("FINAL WRITE")


score.write(
    "musicxml",
    fp=output_file
)


print("DONE")
print(output_file)