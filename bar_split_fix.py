import sys
from music21 import converter, stream, meter, note, chord


input_file = sys.argv[1]
output_file = sys.argv[2]


score = converter.parse(input_file)


# 強制4/4
for p in score.parts:

    p.insert(
        0,
        meter.TimeSignature("4/4")
    )


new_score = stream.Score()


for part in score.parts:

    new_part = stream.Part()

    current_measure = stream.Measure(
        number=1
    )

    duration = 0


    for element in part.flatten().notesAndRests:


        q = element.duration.quarterLength


        # 超過4拍，切開
        if duration + q > 4:

            remain = 4 - duration


            if remain > 0:

                if isinstance(element,note.Note):

                    n = note.Note(
                        element.pitch
                    )
                    n.duration.quarterLength = remain
                    current_measure.append(n)


                elif isinstance(element,chord.Chord):

                    c = chord.Chord(
                        element.pitches
                    )
                    c.duration.quarterLength = remain
                    current_measure.append(c)


            new_part.append(current_measure)


            current_measure = stream.Measure(
                number=current_measure.number+1
            )


            duration = 0


            left = q-remain


            if left>0:

                element.duration.quarterLength=left

                current_measure.append(element)

                duration=left


        else:

            current_measure.append(element)

            duration += q



    if len(current_measure):

        new_part.append(current_measure)



    new_score.append(new_part)



new_score.write(
    "musicxml",
    fp=output_file
)


print("BAR SPLIT OK")