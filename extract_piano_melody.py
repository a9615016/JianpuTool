from music21 import converter, stream, note, chord


def extract_melody(input_file, output_file):

    score = converter.parse(input_file)

    melody = stream.Part()

    events = []


    for part in score.parts:

        for n in part.recurse().notes:

            # 跳過休止
            if isinstance(n, note.Rest):
                continue


            # 和弦取最高音
            if isinstance(n, chord.Chord):

                n = n.sortAscending().notes[-1]


            events.append(n)


    # 依音高排序
    events.sort(
        key=lambda x: x.pitch.midi,
        reverse=True
    )


    # 取較高音區(右手)
    melody_notes = events[:len(events)//2]


    # 依時間排序
    melody_notes.sort(
        key=lambda x: x.offset
    )


    for n in melody_notes:
        melody.append(n)


    melody.write(
        "musicxml",
        fp=output_file
    )


if __name__ == "__main__":

    extract_melody(
        "test.musicxml",
        "twinkle_melody.musicxml"
    )

    print("完成 twinkle_melody.musicxml")