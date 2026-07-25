import music21
import sys


def extract_melody(input_midi, output_midi):

    print("讀取 MIDI")

    score = music21.converter.parse(input_midi)


    best_part = None
    best_score = 0


    print("分析音軌")


    for part in score.parts:

        notes = []

        for n in part.flatten().notes:

            if isinstance(n, music21.note.Note):
                notes.append(n)

            elif isinstance(n, music21.chord.Chord):
                notes.append(
                    n.highestTime
                )


        if len(notes) == 0:
            continue


        avg_pitch = sum(
            n.pitch.midi
            for n in notes
            if hasattr(n, "pitch")
        ) / len(notes)


        score_value = len(notes) * avg_pitch


        print(
            part.partName,
            "notes:",
            len(notes),
            "pitch:",
            avg_pitch
        )


        if score_value > best_score:

            best_score = score_value
            best_part = part



    if best_part is None:
        raise Exception(
            "找不到旋律"
        )


    print(
        "選擇旋律軌"
    )


    new_score = music21.stream.Score()

    new_part = music21.stream.Part()



    for n in best_part.flatten().notes:

        if isinstance(
            n,
            music21.note.Note
        ):

            new_part.append(n)



        elif isinstance(
            n,
            music21.chord.Chord
        ):

            new_part.append(
                music21.note.Note(
                    n.pitches[-1],
                    quarterLength=n.duration.quarterLength
                )
            )



    new_score.append(new_part)


    new_score.write(
        "midi",
        fp=output_midi
    )


    print(
        "完成:",
        output_midi
    )



if __name__ == "__main__":

    extract_melody(
        sys.argv[1],
        sys.argv[2]
    )