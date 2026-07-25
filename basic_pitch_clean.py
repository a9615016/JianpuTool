import music21
import sys



def clean_midi(input_file, output_file):

    print("開始清理 Basic Pitch MIDI")
    print("輸入:", input_file)


    score = music21.converter.parse(input_file)


    new_score = music21.stream.Score()


    for part in score.parts:

        new_part = music21.stream.Part()

        last_pitch = None
        last_note = None


        for element in part.flatten().notes:


            # 移除和弦
            if isinstance(element, music21.chord.Chord):

                note = element.sortAscending()[0]


            else:

                note = element



            pitch = note.pitch.midi


            # 過濾雜訊音域
            if pitch < 40 or pitch > 90:
                continue



            duration = element.duration.quarterLength


            # 移除太短音
            if duration < 0.25:
                continue



            # 合併相同連續音

            if (
                last_pitch == pitch
                and last_note is not None
            ):

                last_note.duration.quarterLength += 0.5

                continue



            n = music21.note.Note(pitch)


            # 簡化節奏
            if duration >= 1:

                n.quarterLength = 1

            else:

                n.quarterLength = 0.5



            new_part.append(n)


            last_pitch = pitch
            last_note = n



        new_score.append(new_part)



    new_score.write(
        "midi",
        fp=output_file
    )


    print("完成:")
    print(output_file)




if __name__ == "__main__":


    if len(sys.argv) < 3:

        print(
            "使用方式:"
        )

        print(
            "python basic_pitch_clean.py input.mid output.mid"
        )

        sys.exit(1)



    clean_midi(
        sys.argv[1],
        sys.argv[2]
    )