from music21 import converter, stream, meter, note, chord
import sys


print("==============================")
print("CLEAN MUSICXML V27")
print("FORCE BAR SPLIT JIANPU FIX")
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
# remove chord
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
# 4/4
# =========================

print("force 4/4")


for part in score.parts:

    part.insert(
        0,
        meter.TimeSignature("4/4")
    )



# =========================
# quantize
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
# FORCE SPLIT CROSS BAR
# =========================

print("split cross measure notes")


for part in score.parts:


    measures = list(
        part.getElementsByClass(stream.Measure)
    )


    new_part = stream.Part()


    for m in measures:


        new_measure = stream.Measure(
            number=m.number
        )


        pos = 0


        for n in m.notesAndRests:


            length = float(
                n.duration.quarterLength
            )


            while length > 0:


                remain = 4 - pos


                take = min(
                    length,
                    remain
                )


                if n.isRest:

                    new_n = note.Rest(
                        quarterLength=take
                    )

                else:

                    new_n = note.Note(
                        n.pitch,
                        quarterLength=take
                    )


                new_measure.append(
                    new_n
                )


                pos += take
                length -= take



                if pos >= 4:

                    pos = 0



        new_part.append(
            new_measure
        )


    part.removeByClass(
        stream.Measure
    )


    for m in new_part:

        part.append(m)



# =========================
# fill rest
# =========================

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



# =========================
# final notation
# =========================

print("clear notation cache")


for part in score.parts:

    part.makeNotation(
        inPlace=True
    )



# =========================
# check
# =========================

print("FINAL CHECK")


bad = False


for m in score.parts[0].getElementsByClass(
    stream.Measure
):


    size = float(
        m.duration.quarterLength
    )


    print(
        "Measure",
        m.number,
        size
    )


    if abs(size-4)>0.01:

        bad=True



if bad:

    print("WARNING measure mismatch")

else:

    print("ALL MEASURES SAFE")



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