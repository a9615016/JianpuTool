from music21 import converter, stream, note, meter
import sys


print("MIDI TO MUSICXML V2.2")


inp = sys.argv[1]
out = sys.argv[2]


score = converter.parse(inp)


new_score = stream.Score()


for part in score.parts:

    new_part = stream.Part()

    new_part.insert(
        0,
        meter.TimeSignature("4/4")
    )


    current_measure = stream.Measure(
        number=1
    )

    pos = 0


    for n in part.recurse().notes:


        dur = round(
            float(n.duration.quarterLength)
            * 4
        ) / 4


        if dur <= 0:
            dur = 0.25



        # 超過小節切開

        while dur > 0:


            remain = 4 - pos


            length = min(
                dur,
                remain
            )


            new_note = note.Note(
                n.pitch,
                quarterLength=length
            )


            current_measure.append(
                new_note
            )


            pos += length
            dur -= length



            if pos >= 4:


                new_part.append(
                    current_measure
                )


                current_measure = stream.Measure(
                    number=current_measure.number+1
                )


                pos = 0



    if len(current_measure.notes):

        new_part.append(
            current_measure
        )


    new_score.append(
        new_part
    )


print("WRITE MUSICXML")


new_score.write(
    "musicxml",
    fp=out
)


print("DONE")