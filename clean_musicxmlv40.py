from music21 import converter, stream, meter, note, chord
import sys


print("==============================")
print("CLEAN MUSICXML V29")
print("REBUILD MEASURE STABLE 4/4")
print("==============================")


if len(sys.argv) < 3:
    print("python clean_musicxml.py input.musicxml output.musicxml")
    sys.exit()


input_file = sys.argv[1]
output_file = sys.argv[2]


print("read")

src = converter.parse(input_file)


# =========================
# create new score
# =========================

new_score = stream.Score()


# =========================
# process parts
# =========================

for src_part in src.parts:


    print("process part")


    new_part = stream.Part()


    new_part.insert(
        0,
        meter.TimeSignature("4/4")
    )


    notes = []


    # collect notes
    for n in src_part.recurse().notesAndRests:


        # remove chord
        if isinstance(n, chord.Chord):

            if len(n.pitches):

                n = note.Note(
                    n.pitches[0]
                )

            else:
                continue


        if n.isNote:

            new_n = note.Note(
                n.pitch
            )

        else:

            new_n = note.Rest()



        # quantize duration

        q = round(
            float(n.duration.quarterLength) / 0.25
        ) * 0.25


        if q <= 0:
            q = 0.25


        new_n.duration.quarterLength = q


        new_n.tie = None
        new_n.beams = []


        notes.append(new_n)



    # =========================
    # rebuild measures
    # =========================

    print("rebuild measures")


    measure_no = 1

    current_measure = stream.Measure(
        number=measure_no
    )


    pos = 0



    for n in notes:


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

                nn = note.Rest(
                    quarterLength=take
                )

            else:

                nn = note.Note(
                    n.pitch,
                    quarterLength=take
                )


            current_measure.append(nn)


            pos += take
            length -= take



            # measure full

            if abs(pos-4) < 0.001:


                new_part.append(
                    current_measure
                )


                measure_no += 1


                current_measure = stream.Measure(
                    number=measure_no
                )


                pos = 0



    # =========================
    # fill last measure
    # =========================

    if pos > 0:


        current_measure.append(
            note.Rest(
                quarterLength=4-pos
            )
        )


        new_part.append(
            current_measure
        )


    new_score.append(
        new_part
    )



# =========================
# final notation
# =========================

print("notation rebuild")


for part in new_score.parts:

    part.makeNotation(
        inPlace=True
    )



# =========================
# check
# =========================

print("FINAL CHECK")


bad = False


for part in new_score.parts:


    for m in part.getElementsByClass(
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


        if abs(size-4)>0.001:

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


new_score.write(
    "musicxml",
    fp=output_file
)


print("DONE")
print(output_file)