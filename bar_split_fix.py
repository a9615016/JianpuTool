import sys
from music21 import converter, stream, note, chord, meter, duration


input_file = sys.argv[1]
output_file = sys.argv[2]


score = converter.parse(input_file)


new_score = stream.Score()



def make_duration(obj, ql):

    obj.duration = duration.Duration(
        ql
    )

    # 強制產生 type
    obj.duration.quarterLength = ql

    return obj



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



            make_duration(
                obj,
                take
            )


            measure.append(
                obj
            )


            used += take

            remaining -= take



            if used >= 4.0 - 0.0001:


                new_part.append(
                    measure
                )


                measure_no += 1


                measure = stream.Measure(
                    number=measure_no
                )


                used = 0



    if len(measure.notesAndRests):


        if used < 4:

            r = note.Rest()

            make_duration(
                r,
                4-used
            )

            measure.append(r)



        new_part.append(
            measure
        )


    new_score.append(
        new_part
    )



# 重新排譜

new_score.makeNotation(
    inPlace=True
)


# 再檢查一次 duration

for p in new_score.parts:

    for n in p.flatten().notesAndRests:

        if not n.duration.type:

            n.duration = duration.Duration(
                n.duration.quarterLength
            )



new_score.write(
    "musicxml",
    fp=output_file
)


print(
    "BAR SPLIT OK"
)