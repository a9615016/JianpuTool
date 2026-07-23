from music21 import converter, stream, note, chord


def extract_melody(
    input_xml,
    output_xml
):

    score = converter.parse(
        input_xml
    )


    melody = stream.Part()


    # 取第一軌
    if len(score.parts) > 0:

        part = score.parts[0]

    else:

        part = score



    for element in part.recurse():

        if isinstance(element, note.Note):

            melody.append(
                element
            )


        elif isinstance(element, chord.Chord):

            # 和弦只取最高音
            highest = max(
                element.notes,
                key=lambda n: n.pitch.midi
            )

            melody.append(
                highest
            )



    melody.write(
        "musicxml",
        fp=output_xml
    )


    return output_xml