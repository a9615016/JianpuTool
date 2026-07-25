import music21
import sys


def extract_melody(input_midi, output_midi):

    print("開始 Melody Extractor")

    score = music21.converter.parse(input_midi)


    all_notes = []


    print("收集音符")


    for part in score.parts:

        for n in part.flatten().notes:


            if isinstance(n, music21.note.Note):

                all_notes.append(n)


            elif isinstance(n, music21.chord.Chord):

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
        "總音符:",
        len(all_notes)
    )


    # 按時間排序

    all_notes.sort(
        key=lambda n:n.offset
    )


    melody = []


    current_time = None
    current_group = []



    for n in all_notes:


        if current_time is None:

            current_time = n.offset



        if n.offset != current_time:


            if current_group:

                # 同時間只留最高音

                highest = max(
                    current_group,
                    key=lambda x:x.pitch.midi
                )

                melody.append(highest)


            current_group = []

            current_time = n.offset



        current_group.append(n)



    if current_group:

        highest = max(
            current_group,
            key=lambda x:x.pitch.midi
        )

        melody.append(highest)



    print(
        "旋律音符:",
        len(melody)
    )



    # 建立新的 MIDI

    result = music21.stream.Part()


    for n in melody:


        # 移除左手低音

        if n.pitch.midi >= 60:

            result.append(n)



    new_score = music21.stream.Score()

    new_score.append(result)



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