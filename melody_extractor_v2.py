import music21
import sys


def extract_piano_melody(input_midi, output_midi):

    print("開始 Piano Melody Extractor v2")
    print("輸入:", input_midi)


    score = music21.converter.parse(
        input_midi
    )


    all_notes = []


    print("讀取所有音符")


    for part in score.parts:

        for n in part.flatten().notes:


            if isinstance(
                n,
                music21.note.Note
            ):

                all_notes.append(n)



            elif isinstance(
                n,
                music21.chord.Chord
            ):

                highest = max(
                    n.pitches,
                    key=lambda p:p.midi
                )


                all_notes.append(
                    music21.note.Note(
                        highest,
                        quarterLength=n.duration.quarterLength
                    )
                )



    print(
        "原始音符數:",
        len(all_notes)
    )



    # 依時間排序

    all_notes.sort(
        key=lambda x:x.offset
    )



    melody = []


    current_offset = None
    group = []



    for n in all_notes:


        if current_offset is None:

            current_offset = n.offset



        if n.offset != current_offset:


            if group:

                highest = max(
                    group,
                    key=lambda x:x.pitch.midi
                )


                melody.append(
                    highest
                )


            group = []
            current_offset = n.offset



        group.append(n)



    if group:

        highest = max(
            group,
            key=lambda x:x.pitch.midi
        )

        melody.append(
            highest
        )



    print(
        "最高音旋律:",
        len(melody)
    )



    # 建立新的旋律 MIDI

    result_part = music21.stream.Part()



    for n in melody:


        # 移除左手伴奏
        # 小星星旋律通常 C4 以上

        if n.pitch.midi >= 60:

            result_part.append(
                n
            )



    print(
        "最後旋律:",
        len(result_part.notes)
    )



    print("旋律內容:")


    for n in result_part.notes[:40]:

        print(
            n.pitch.nameWithOctave,
            n.duration.quarterLength
        )



    new_score = music21.stream.Score()

    new_score.append(
        result_part
    )


    new_score.write(
        "midi",
        fp=output_midi
    )


    print(
        "完成:",
        output_midi
    )





if __name__ == "__main__":


    if len(sys.argv) < 3:

        print(
            "python melody_extractor_v2.py input.mid output.mid"
        )

        sys.exit(1)



    extract_piano_melody(
        sys.argv[1],
        sys.argv[2]
    )