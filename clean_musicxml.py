from music21 import converter, stream, note, chord, meter, duration
import sys


print("==============================")
print("CLEAN MUSICXML V85")
print("JIANPU_LY STRICT 4/4 REBUILDER")
print("==============================")


input_file = sys.argv[1]

if len(sys.argv) >= 3:
    output_file = sys.argv[2]
else:
    output_file = "clean.musicxml"



score = converter.parse(input_file)

print("READ")


# ==========================
# duration allowed
# ==========================

allowed = [
    4,
    2,
    1,
    0.5,
    0.25
]


def quantize_length(x):

    return min(
        allowed,
        key=lambda y: abs(y-x)
    )



# ==========================
# rebuild one part
# ==========================

new_score = stream.Score()


for part in score.parts:

    new_part = stream.Part()

    new_part.append(
        meter.TimeSignature("4/4")
    )


    print("PROCESS PART")


    current_measure = stream.Measure(
        number=1
    )

    current_time = 0.0


    elements = []


    for e in part.recurse():

        if isinstance(e, note.Note):

            elements.append(e)

        elif isinstance(e, chord.Chord):

            n = e.notes[0]

            elements.append(n)



    for n in elements:


        # remove notation

        n.tie = None

        n.beams.fill(0)


        remain = float(
            n.duration.quarterLength
        )


        if remain <= 0:
            continue



        while remain > 0:


            space = 4.0 - current_time


            take = min(
                remain,
                space
            )


            take = quantize_length(take)



            if take <= 0:
                break



            new_note = note.Note(
                n.pitch
            )

            new_note.duration = duration.Duration(
                take
            )


            current_measure.append(
                new_note
            )


            current_time += take

            remain -= take



            # full measure

            if current_time >= 4.0 - 0.001:


                new_part.append(
                    current_measure
                )


                current_measure = stream.Measure(
                    number=len(
                        new_part.getElementsByClass(
                            "Measure"
                        )
                    ) + 1
                )


                current_time = 0.0



    # ==========================
    # fill last measure
    # ==========================

    if current_time > 0:


        rest = note.Rest(
            quarterLength=4-current_time
        )

        current_measure.append(
            rest
        )


        new_part.append(
            current_measure
        )



    new_score.append(
        new_part
    )



print("REBUILD COMPLETE")



# ==========================
# FINAL CHECK
# ==========================

print("FINAL CHECK")


for p in new_score.parts:

    for m in p.getElementsByClass(
        "Measure"
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


        if abs(total-4.0)>0.01:

            print(
                "ERROR MEASURE",
                m.number,
                total
            )



# ==========================
# WRITE
# ==========================

new_score.write(
    "musicxml",
    fp=output_file
)


print("================")
print("DONE")
print(output_file)
print("================")