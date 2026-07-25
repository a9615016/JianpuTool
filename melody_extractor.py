import music21
import sys


def extract_melody(input_midi, output_midi):

    print("開始 Melody Extractor")
    print("輸入:", input_midi)


    score = music21.converter.parse(
        input_midi
    )


    candidates = []


    print("分析 MIDI 軌道")


    for part in score.parts:

        notes = []


        for n in part.flatten().notes:


            # 單音
            if isinstance(
                n,
                music21.note.Note
            ):

                notes.append(n)



            # 和弦取最高音
            elif isinstance(
                n,
                music21.chord.Chord
            ):

                highest = max(
                    n.pitches,
                    key=lambda p: p.midi
                )


                notes.append(
                    music21.note.Note(
                        highest,
                        quarterLength=n.duration.quarterLength
                    )
                )



        if len(notes) < 5:
            continue



        avg_pitch = sum(
            n.pitch.midi
            for n in notes
        ) / len(notes)


        note_count = len(notes)


        score_value = (
            note_count * 0.7
            +
            avg_pitch * 3
        )


        print(
            "Track:",
            part.partName,
            "notes:",
            note_count,
            "avg:",
            round(avg_pitch,2),
            "score:",
            round(score_value,2)
        )


        candidates.append(
            (
                score_value,
                part
            )
        )



    if not candidates:

        raise Exception(
            "找不到旋律軌"
        )



    candidates.sort(
        key=lambda x:x[0],
        reverse=True
    )


    melody_part = candidates[0][1]


    print(
        "選擇最佳旋律軌"
    )


    new_score = music21.stream.Score()

    new_part = music21.stream.Part()



    for n in melody_part.flatten().notes:


        if isinstance(
            n,
            music21.note.Note
        ):


            # 移除低音伴奏
            if n.pitch.midi >= 48:

                new_part.append(
                    n
                )



        elif isinstance(
            n,
            music21.chord.Chord
        ):


            highest = max(
                n.pitches,
                key=lambda p:p.midi
            )


            if highest.midi >= 48:

                new_part.append(
                    music21.note.Note(
                        highest,
                        quarterLength=n.duration.quarterLength
                    )
                )



    new_score.append(
        new_part
    )


    new_score.write(
        "midi",
        fp=output_midi
    )


    print(
        "完成:",
        output_midi
    )


    return output_midi



if __name__ == "__main__":

    if len(sys.argv) < 3:

        print(
            "python melody_extractor.py input.mid output.mid"
        )

        sys.exit(1)


    extract_melody(
        sys.argv[1],
        sys.argv[2]
    )