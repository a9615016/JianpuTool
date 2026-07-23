from music21 import converter, stream, note, chord


def extract_melody(input_file, output_file):

    score = converter.parse(input_file)

    melody = stream.Part()

    notes = []

    for part in score.parts:

        for n in part.recurse().notes:

            if isinstance(n, note.Rest):
                continue


            if isinstance(n, chord.Chord):

                n = n.sortAscending().notes[-1]


            # 右手音域
            if n.pitch.midi >= 60:

                notes.append(n)


    # 保留時間順序
    notes.sort(
        key=lambda x: x.offset
    )


    for n in notes:
        melody.append(n)


    melody.write(
        "musicxml",
        fp=output_file
    )


if __name__ == "__main__":

    extract_melody(
        "test.musicxml",
        "twinkle_melody_v3.musicxml"
    )

    print("完成 twinkle_melody_v3.musicxml")