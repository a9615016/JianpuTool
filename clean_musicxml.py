from music21 import converter, stream, meter, note, chord
import sys


print("==============================")
print("CLEAN MUSICXML V30")
print("REBUILD SCORE JIANPU FIX")
print("==============================")


if len(sys.argv) < 3:
    print(
        "python clean_musicxml.py input.musicxml output.musicxml"
    )
    sys.exit()


input_file = sys.argv[1]
output_file = sys.argv[2]


print("read")

old_score = converter.parse(input_file)



# ==========================
# create new score
# ==========================

print("rebuild new score")


new_score = stream.Score()



for old_part in old_score.parts:


    new_part = stream.Part()


    new_part.insert(
        0,
        meter.TimeSignature("4/4")
    )


    # collect notes

    elements=[]


    for e in old_part.recurse().notesAndRests:


        if isinstance(e, chord.Chord):

            n = note.Note(
                e.pitches[0]
            )

            n.duration = e.duration

            elements.append(n)


        else:

            elements.append(e)



    # ======================
    # quantize
    # ======================

    print("quantize")


    events=[]


    for e in elements:


        q = round(
            float(e.duration.quarterLength) / 0.25
        ) * 0.25


        if q <= 0:

            q = 0.25


        if isinstance(e, note.Rest):

            new_e = note.Rest(
                quarterLength=q
            )


        else:

            new_e = note.Note(
                e.pitch,
                quarterLength=q
            )


        events.append(new_e)



    # ======================
    # rebuild measures
    # ======================

    print("create measures")


    measure_no = 1

    m = stream.Measure(
        number=measure_no
    )


    pos = 0


    for e in events:


        length = float(
            e.duration.quarterLength
        )


        while length > 0:


            remain = 4 - pos


            take = min(
                remain,
                length
            )


            if isinstance(e, note.Rest):

                x = note.Rest(
                    quarterLength=take
                )

            else:

                x = note.Note(
                    e.pitch,
                    quarterLength=take
                )


            m.append(x)


            pos += take
            length -= take



            if pos >= 4:


                # finish measure

                new_part.append(m)


                measure_no += 1


                m = stream.Measure(
                    number=measure_no
                )


                pos = 0



    # last measure

    if pos > 0:


        m.append(
            note.Rest(
                quarterLength=4-pos
            )
        )


        new_part.append(m)



    new_score.append(
        new_part
    )



# ==========================
# final check
# ==========================

print("FINAL CHECK")


bad=False


for part in new_score.parts:


    for m in part.getElementsByClass(
        stream.Measure
    ):


        size=float(
            m.duration.quarterLength
        )


        print(
            "Measure",
            m.number,
            size
        )


        if abs(size-4)>0.001:

            bad=True



if bad:

    print(
        "WARNING measure mismatch"
    )

else:

    print(
        "ALL MEASURES SAFE"
    )



# ==========================
# write
# ==========================

print("FINAL WRITE")


new_score.write(
    "musicxml",
    fp=output_file
)


print("DONE")
print(output_file)