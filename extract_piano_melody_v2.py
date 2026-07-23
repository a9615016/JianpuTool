from music21 import converter, stream, note, chord
from collections import defaultdict


def extract_melody(input_file, output_file):

    score = converter.parse(input_file)

    melody = stream.Part()

    events = defaultdict(list)


    # 收集所有音符
    for part in score.parts:

        for n in part.recurse().notes:

            if isinstance(n, note.Rest):
                continue


            if isinstance(n, chord.Chord):

                for p in n.pitches:
                    events[n.offset].append(
                        note.Note(
                            p,
                            quarterLength=n.quarterLength
                        )
                    )

            else:

                events[n.offset].append(n)


    # 每個時間點選最高音
    melody_notes = []


    for offset in sorted(events.keys()):

        notes = events[offset]

        highest = max(
            notes,
            key=lambda x: x.pitch.midi
        )

        highest.offset = offset

        melody_notes.append(highest)


    # 輸出
    for n in melody_notes:
        melody.append(n)


    melody.write(
        "musicxml",
        fp=output_file
    )


if __name__ == "__main__":

    extract_melody(
        "test.musicxml",
        "twinkle_melody_v2.musicxml"
    )

    print("完成 twinkle_melody_v2.musicxml")