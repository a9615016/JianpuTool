from music21 import converter, stream, note, chord, meter, bar
import sys
import os


print("==============================")
print("CLEAN MUSICXML V27 JIANPU")
print("==============================")


if len(sys.argv) < 3:
    print("usage: python clean_musicxml.py input.musicxml output.musicxml")
    sys.exit()


input_file = sys.argv[1]
output_file = sys.argv[2]


print("READ")

score = converter.parse(input_file)



# ==========================
# create clean score
# ==========================

new_score = stream.Score()



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
        key=lambda y: abs(y-x)
    )



for old_part in score.parts:

    print("PROCESS PART")

    new_part = stream.Part()


    # force 4/4
    new_part.insert(
        0,
        meter.TimeSignature("4/4")
    )


    current_measure = stream.Measure()
    current_measure.number = 1

    beat_used = 0


    for obj in old_part.recurse().notes:


        # ======================
        # chord -> single note
        # ======================

        if isinstance(obj, chord.Chord):

            n = note.Note(
                obj.pitches[0]
            )

            dur = obj.duration.quarterLength

        else:

            n = note.Note(
                obj.pitch
            )

            dur = obj.duration.quarterLength



        # quantize

        dur = quantize(
            float(dur)
        )


        remaining = dur


        # ======================
        # split measure
        # ======================

        while remaining > 0:


            space = 4 - beat_used


            use = min(
                remaining,
                space
            )


            nn = note.Note(
                n.pitch
            )

            nn.duration.quarterLength = use


            current_measure.append(
                nn
            )


            beat_used += use
            remaining -= use



            if beat_used >= 4:


                new_part.append(
                    current_measure
                )


                current_measure = stream.Measure()

                current_measure.number = (
                    len(new_part.getElementsByClass("Measure"))
                    + 1
                )

                beat_used = 0



    # ======================
    # fill rest
    # ======================

    if beat_used > 0:

        r = note.Rest()

        r.duration.quarterLength = (
            4 - beat_used
        )

        current_measure.append(r)

        new_part.append(
            current_measure
        )


    new_score.append(
        new_part
    )



# ==========================
# final check
# ==========================


print("FINAL CHECK")


for m in new_score.parts[0].getElementsByClass("Measure"):

    print(
        "Measure",
        m.number,
        float(m.duration.quarterLength)
    )



print("WRITE")


new_score.write(
    "musicxml",
    fp=output_file
)


print("DONE")
print(output_file)