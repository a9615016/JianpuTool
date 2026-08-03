import sys
from music21 import converter, stream, note, meter


input_file = sys.argv[1]
output_file = sys.argv[2]


score = converter.parse(input_file)


for part in score.parts:

    part.makeMeasures(
        inPlace=True
    )


    new_measures = []


    for measure in part.getElementsByClass(
        stream.Measure
    ):

        offset = 0

        new_measure = stream.Measure(
            number=measure.number
        )


        for element in measure.notesAndRests:


            dur = element.duration.quarterLength


            # 超過小節
            if offset + dur > 4:


                first = 4 - offset


                second = dur - first


                n1 = element.clone()

                n2 = element.clone()


                n1.duration.quarterLength = first

                n2.duration.quarterLength = second


                if isinstance(n1, note.Note):

                    n1.tie = None

                    n2.tie = None


                new_measure.append(
                    n1
                )


                # 下一小節處理
                new_measure.append(
                    n2
                )


            else:

                new_measure.append(
                    element
                )


            offset += dur


        new_measures.append(
            new_measure
        )


    part.removeByClass(
        stream.Measure
    )


    for m in new_measures:

        part.append(m)



# 再固定4/4

for part in score.parts:

    part.insert(
        0,
        meter.TimeSignature("4/4")
    )


score.write(
    "musicxml",
    fp=output_file
)


print("split cross bar OK")