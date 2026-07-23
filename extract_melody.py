from music21 import converter, stream, note, chord


def extract_melody(input_xml, output_xml):

    score = converter.parse(input_xml)

    melody = stream.Part()

    for part in score.parts:

        for element in part.recurse():

            if isinstance(element, chord.Chord):

                # 取和弦最高音
                highest = element.sortAscending().notes[-1]

                melody.append(
                    highest
                )

            elif isinstance(element, note.Note):

                melody.append(element)


    melody.write(
        "musicxml",
        fp=output_xml
    )


if __name__ == "__main__":

    extract_melody(
        "test.musicxml",
        "melody.musicxml"
    )

    print("完成 melody.musicxml")