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


    used = 0.0



    for el in old_part.flatten().notesAndRests:


        remaining = float(
            el.duration.quarterLength
        )


        while remaining > 0:


            space = 4.0 - used


            take = min(
                space,
                remaining
            )


            # 建立新物件

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



            # 設定長度
            obj.duration.quarterLength = take


            measure.append(
                obj
            )


            used += take

            remaining -= take



            # 滿小節

            if used >= 4.0 - 0.0001:


                new_part.append(
                    measure
                )


                measure_no += 1


                measure = stream.Measure(
                    number=measure_no
                )


                used = 0.0



    # 補最後小節

    if len(measure.notesAndRests):


        if used < 4:


            r = note.Rest()

            r.duration.quarterLength = (
                4.0 - used
            )

            measure.append(r)



        new_part.append(
            measure
        )



    new_score.append(
        new_part
    )



# 重新整理 notation

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