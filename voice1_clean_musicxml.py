from music21 import converter, stream, note, chord


def clean_voice1(input_file, output_file):

    score = converter.parse(input_file)

    output = stream.Score()

    for part in score.parts:

        new_part = stream.Part()

        # 優先找 Voice
        voices = part.voices

        if len(voices) > 0:

            # 取第一個 Voice (通常右手)
            voice = voices[0]

            for n in voice.recurse().notes:

                if isinstance(n, chord.Chord):
                    # 和弦取最高音
                    new_part.append(
                        n.sortAscending().notes[-1]
                    )

                else:
                    new_part.append(n)

        else:

            # 沒有 Voice 標記
            for n in part.recurse().notes:

                if isinstance(n, chord.Chord):

                    new_part.append(
                        n.sortAscending().notes[-1]
                    )

                else:

                    new_part.append(n)


        output.append(new_part)


    output.write(
        "musicxml",
        fp=output_file
    )


if __name__ == "__main__":

    clean_voice1(
        "test.musicxml",
        "voice1_clean.musicxml"
    )

    print("完成 voice1_clean.musicxml")