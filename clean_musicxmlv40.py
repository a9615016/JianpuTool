from music21 import converter, stream, meter, note, chord
import sys


print("==============================")
print("CLEAN MUSICXML V28")
print("STABLE 4/4 JIANPU FIX")
print("==============================")


if len(sys.argv) < 3:
    print(
        "python clean_musicxml.py input.musicxml output.musicxml"
    )
    sys.exit()


input_file = sys.argv[1]
output_file = sys.argv[2]


print("read")

score = converter.parse(
    input_file
)


# =========================
# remove chords
# =========================

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



# =========================
# remove notation
# =========================

print("remove beams")


for n in score.recurse().notes:

    n.beams = []



print("remove ties")


for n in score.recurse().notes:

    n.tie = None



# =========================
# force 4/4
# =========================

print("force 4/4")


for part in score.parts:

    part.insert(
        0,
        meter.TimeSignature("4/4")
    )



# =========================
# quantize duration
# =========================

print("duration quantize")


for n in score.recurse().notesAndRests:


    q = round(
        float(n.duration.quarterLength) / 0.25
    ) * 0.25


    if q <= 0:

        q = 0.25


    n.duration.quarterLength = q



# =========================
# rebuild measures
# =========================

print("rebuild measures")


for part in score.parts:

    part.makeMeasures(
        inPlace=True
    )



# =========================
# split long notes
# =========================

print("split cross measure notes")


for part in score.parts:

    for m in list(
        part.getElementsByClass(stream.Measure)
    ):

        for n in list(
            m.notesAndRests
        ):


            if n.duration.quarterLength > 4:


                print(
                    "split:",
                    n,
                    n.duration.quarterLength
                )


                n.splitAtDurations(
                    inPlace=True
                )



# =========================
# fill rest
# =========================

print("fill measure rest")


for part in score.parts:


    for m in part.getElementsByClass(
        stream.Measure
    ):


        length = sum(
            float(x.duration.quarterLength)
            for x in m.notesAndRests
        )


        if length < 4:


            m.append(
                note.Rest(
                    quarterLength=4-length
                )
            )



# =========================
# refresh notation
# =========================

print("clear notation cache")


for part in score.parts:

    part.makeMeasures(
        inPlace=True
    )

    part.makeNotation(
        inPlace=True
    )



# =========================
# final check
# =========================

print("FINAL CHECK")


bad = False


for m in score.parts[0].getElementsByClass(
    stream.Measure
):


    size = sum(
        float(x.duration.quarterLength)
        for x in m.notesAndRests
    )


    print(
        "Measure",
        m.number,
        size
    )


    if abs(size-4)>0.01:

        bad = True



if bad:

    print(
        "WARNING measure mismatch"
    )

else:

    print(
        "ALL MEASURES SAFE"
    )



# =========================
# write
# =========================

print("FINAL WRITE")


score.write(
    "musicxml",
    fp=output_file
)


print("DONE")
print(output_file)