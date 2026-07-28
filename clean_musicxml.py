from music21 import converter, stream, meter, note, chord
import sys


print("==============================")
print("CLEAN MUSICXML V30")
print("FINAL BAR NORMALIZE JIANPU FIX")
print("==============================")


if len(sys.argv) < 3:
    print("python clean_musicxml.py input.musicxml output.musicxml")
    sys.exit()


input_file = sys.argv[1]
output_file = sys.argv[2]


print("read")

src = converter.parse(input_file)


new_score = stream.Score()



for src_part in src.parts:

    print("process part")

    new_part = stream.Part()


    new_part.insert(
        0,
        meter.TimeSignature("4/4")
    )


    notes = []


    for n in src_part.recurse().notesAndRests:


        # chord -> first note

        if isinstance(n, chord.Chord):

            if len(n.pitches):

                pitch = n.pitches[0]

            else:
                continue

        elif n.isNote:

            pitch = n.pitch

        else:

            pitch = None



        # quantize

        q = round(
            float(n.duration.quarterLength) / 0.25
        ) * 0.25


        if q <= 0:

            q = 0.25



        if pitch:

            nn = note.Note(
                pitch,
                quarterLength=q
            )

        else:

            nn = note.Rest(
                quarterLength=q
            )


        nn.tie = None
        nn.beams = []


        notes.append(nn)



    print("rebuild measures")


    measure_no = 1

    m = stream.Measure(
        number=measure_no
    )


    pos = 0



    for n in notes:


        remain_note = float(
            n.duration.quarterLength
        )


        while remain_note > 0:


            remain_bar = 4 - pos


            take = min(
                remain_note,
                remain_bar
            )


            if n.isRest:

                x = note.Rest(
                    quarterLength=take
                )

            else:

                x = note.Note(
                    n.pitch,
                    quarterLength=take
                )


            m.append(x)


            pos += take
            remain_note -= take



            if abs(pos-4) < 0.001:


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



# =========================
# FINAL BAR NORMALIZE
# =========================

print("FINAL BAR NORMALIZE")


for part in new_score.parts:


    for m in list(
        part.getElementsByClass(stream.Measure)
    ):


        total = sum(
            float(x.duration.quarterLength)
            for x in m.notesAndRests
        )


        print(
            "CHECK BAR",
            m.number,
            total
        )


        # too long

        if total > 4.0:


            overflow = total - 4.0


            for x in reversed(
                list(m.notesAndRests)
            ):


                if overflow <= 0:
                    break


                d = float(
                    x.duration.quarterLength
                )


                cut = min(
                    d,
                    overflow
                )


                remain = d-cut


                if remain <= 0:

                    m.remove(x)

                else:

                    x.duration.quarterLength = remain


                overflow -= cut



        # too short

        elif total < 4.0:


            m.append(
                note.Rest(
                    quarterLength=4-total
                )
            )



# =========================
# notation
# =========================

print("clear notation cache")


for part in new_score.parts:

    part.makeMeasures(
        inPlace=True
    )

    part.makeNotation(
        inPlace=True
    )



# =========================
# FINAL CHECK
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

    print("WARNING measure mismatch")

else:

    print("ALL MEASURES SAFE")



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