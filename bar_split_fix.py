import sys
from music21 import converter, stream, note, chord, meter


input_file = sys.argv[1]
output_file = sys.argv[2]


score = converter.parse(input_file)


new_score = stream.Score()



for old_part in score.parts:


    new_part = stream.Part()


    new_part.insert(
        0,
        meter.TimeSignature("4/4")
    )


    measure_no = 1

    measure = stream.Measure(
        number=measure_no
    )


    beat_used = 0



    for el in old_part.flatten().notesAndRests:


        total = float(
            el.duration.quarterLength
        )


        while total > 0:


            space = 4 - beat_used


            length = min(
                space,
                total
            )


            # 建立新元素

            if isinstance(el, note.Note):

                obj = note.Note(
                    el.pitch
                )


            elif isinstance(el, chord.Chord):

                obj = chord.Chord(
                    el.pitches
                )


            else:

                obj = note.Rest()



            obj.duration.quarterLength = length


            # ⭐重要
            obj.duration.clear()
            obj.duration.quarterLength = length
            obj.duration.type = None
            obj.duration.updateTuplet()



            measure.append(
                obj
            )



            beat_used += length

            total -= length



            if beat_used >= 4 - 0.0001:


                new_part.append(
                    measure
                )


                measure_no += 1


                measure = stream.Measure(
                    number=measure_no
                )


                beat_used = 0



    if len(measure.elements):

        remain = 4 - beat_used


        if remain > 0:

            r = note.Rest()

            r.duration.quarterLength = remain

            r.duration.type = None

            r.duration.updateTuplet()

            measure.append(r)



        new_part.append(
            measure
        )



    new_score.append(
        new_part
    )



# 重新做 notation

new_score.makeNotation(
    inPlace=True
)



new_score.write(
    "musicxml",
    fp=output_file
)


print(
    "BAR SPLIT OK"
)