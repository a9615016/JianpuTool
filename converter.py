import music21
import os


def midi_to_musicxml(input_file, output_file):

    print("開始 MIDI -> MusicXML")


    # ==========================
    # 讀 MIDI
    # ==========================

    score = music21.converter.parse(input_file)


    print("parts:", len(score.parts))



    # ==========================
    # 取第一聲部
    # ==========================

    if len(score.parts) > 0:

        melody = score.parts[0]

    else:

        melody = score



    # ==========================
    # 移除 chord
    # ==========================

    new_stream = music21.stream.Part()


    for element in melody.flatten():

        if isinstance(
            element,
            music21.note.Note
        ):

            n = music21.note.Note(
                element.pitch
            )

            n.duration = element.duration

            new_stream.append(n)



        elif isinstance(
            element,
            music21.chord.Chord
        ):

            # 只取最高音
            n = music21.note.Note(
                element.pitches[-1]
            )

            n.duration = element.duration

            new_stream.append(n)



        elif isinstance(
            element,
            music21.note.Rest
        ):

            r = music21.note.Rest()

            r.duration = element.duration

            new_stream.append(r)



    melody = new_stream



    # ==========================
    # 限制音域
    # ==========================

    for n in melody.notes:

        if n.pitch.octave < 3:

            n.pitch.octave = 3


        if n.pitch.octave > 6:

            n.pitch.octave = 6



    # ==========================
    # 清除所有 metadata
    # ==========================

    melody.metadata = None



    # ==========================
    # 固定拍號
    # ==========================

    melody.insert(
        0,
        music21.meter.TimeSignature("4/4")
    )



    # ==========================
    # 固定調性
    # ==========================

    melody.insert(
        0,
        music21.key.Key("C")
    )



    # ==========================
    # 移除不必要 voice
    # ==========================

    for v in melody.recurse().getElementsByClass(
        music21.stream.Voice
    ):

        v.activeSite.remove(v)



    # ==========================
    # 輸出 MusicXML
    # ==========================

    melody.write(
        "musicxml",
        fp=output_file
    )


    print(
        "完成:",
        output_file
    )



if __name__ == "__main__":


    midi_to_musicxml(
        "input.mid",
        "output.musicxml"
    )