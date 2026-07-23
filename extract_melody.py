from music21 import converter, stream


def extract_melody(input_xml, output_xml):

    score = converter.parse(input_xml)

    melody = stream.Part()

    melody.id = "Melody"


    notes = []


    # 收集所有音符
    for element in score.recurse().notes:

        if element.isChord:

            # 和弦取最高音
            n = element.sortAscending().notes[-1]

            notes.append(n)

        else:

            notes.append(element)



    # 建立單旋律
    for n in notes:

        melody.append(n)



    new_score = stream.Score()

    new_score.append(melody)


    new_score.write(
        "musicxml",
        fp=output_xml
    )


    return output_xml