import music21
import sys
import os


def extract_melody(input_midi, output_midi):

    print("開始抽取主旋律")
    print("輸入:", input_midi)


    score = music21.converter.parse(
        input_midi
    )


    melody_notes = []


    # 收集所有音符
    for part in score.parts:

        for element in part.flatten().notes:

            if isinstance(
                element,
                music21.note.Note
            ):

                melody_notes.append(
                    element
                )


            elif isinstance(
                element,
                music21.chord.Chord
            ):

                # 和弦取最高音
                highest = element.sortAscending()[-1]

                melody_notes.append(
                    music21.note.Note(
                        highest.pitch,
                        quarterLength=element.duration.quarterLength
                    )
                )



    if len(melody_notes) == 0:

        raise Exception(
            "找不到音符"
        )


    print(
        "原始音符數:",
        len(melody_notes)
    )


    # 依時間排序
    melody_notes.sort(
        key=lambda n:n.offset
    )


    # 建立新樂譜
    new_score = music21.stream.Score()

    part = music21.stream.Part()


    for n in melody_notes:

        part.append(n)



    new_score.append(part)



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


    if len(sys.argv)<3:

        print(
            "使用方式:"
        )

        print(
            "python melody_extractor.py input.mid output.mid"
        )

        sys.exit(1)


    extract_melody(
        sys.argv[1],
        sys.argv[2]
    )