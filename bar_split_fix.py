import sys
from music21 import converter, stream, note, chord, meter


input_file = sys.argv[1]
output_file = sys.argv[2]


score = converter.parse(input_file)


new_score = stream.Score()


for old_part in score.parts:


    new_part = stream.Part()


    # 4/4
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


        dur = float(
            el.duration.quarterLength
        )


        remaining = dur


        while remaining > 0:


            space = 4 - beat_used


            take = min(
                space,
                remaining
            )


            # 重新建立物件
            if isinstance(el, note.Note):

                n = note.Note(
                    el.pitch
                )

                n.duration.quarterLength = take

                measure.append(n)


            elif isinstance(el, chord.Chord):

                c = chord.Chord(
                    el.pitches
                )

                c.duration.quarterLength = take

                measure.append(c)


            elif isinstance(el, note.Rest):

                r = note.Rest()

                r.duration.quarterLength = take

                measure.append(r)



            beat_used += take
            remaining -= take



            # 滿4拍
            if beat_used >= 4:


                new_part.append(
                    measure
                )


                measure_no += 1


                measure = stream.Measure(
                    number=measure_no
                )


                beat_used = 0



    # 最後不足補休止

    if beat_used > 0:

        rest = note.Rest()

        rest.duration.quarterLength = 4 - beat_used

        measure.append(rest)


        new_part.append(
            measure
        )



    new_score.append(
        new_part
    )



# 輸出
new_score.write(
    "musicxml",
    fp=output_file
)


print(
    "BAR SPLIT OK"
)