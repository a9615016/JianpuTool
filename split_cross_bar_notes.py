from music21 import converter, note, chord, stream
import sys
import copy


input_file = sys.argv[1]
output_file = sys.argv[2]


score = converter.parse(input_file)


new_score = stream.Score()


for part in score.parts:

    new_part = stream.Part()

    for measure in part.getElementsByClass('Measure'):

        new_measure = stream.Measure(
            number=measure.number
        )


        for element in measure.notesAndRests:


            # REST 不切割
            if isinstance(element, note.Rest):

                new_measure.append(
                    copy.deepcopy(element)
                )

                continue


            # NOTE / CHORD
            obj = copy.deepcopy(element)


            new_measure.append(obj)



        new_score.append(new_part)


        new_part.append(new_measure)



new_score.write(
    "musicxml",
    fp=output_file
)


print("跨小節修正完成")