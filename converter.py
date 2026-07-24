import os
import music21


def midi_to_musicxml(input_file):

    print("開始 MIDI → MusicXML")
    print("輸入:", input_file)


    base = os.path.splitext(input_file)[0]
    output_file = base + ".musicxml"


    # 讀 MIDI
    score = music21.converter.parse(
        input_file
    )


    print(
        "MIDI 聲部:",
        len(score.parts)
    )


    # ==========================
    # 找主旋律
    # ==========================

    best_part = None
    max_notes = 0


    for part in score.parts:

        notes = len(
            part.recurse().notes
        )


        print(
            "part:",
            part.id,
            "notes:",
            notes
        )


        if notes > max_notes:

            max_notes = notes
            best_part = part



    if best_part is None:

        best_part = score



    melody = best_part



    # ==========================
    # 移除和弦
    # ==========================

    for chord in list(
        melody.recurse().getElementsByClass(
            music21.chord.Chord
        )
    ):

        note = music21.note.Note(
            chord.pitches[-1]
        )

        chord.activeSite.replace(
            chord,
            note
        )



    # ==========================
    # 八度限制
    # ==========================

    for note in melody.recurse().notes:


        if note.pitch.octave < 4:

            note.pitch.octave = 4


        if note.pitch.octave > 6:

            note.pitch.octave = 6



    # ==========================
    # 節奏量化
    # ==========================

    melody.quantize(
        quarterLengthDivisors=[
            1,
            2,
            4
        ]
    )



    # ==========================
    # C大調
    # ==========================

    melody.insert(
        0,
        music21.key.Key("C")
    )


    melody.insert(
        0,
        music21.meter.TimeSignature("4/4")
    )



    # ==========================
    # 輸出
    # ==========================

    melody.write(
        "musicxml",
        fp=output_file
    )


    print(
        "完成:",
        output_file
    )


    return output_file



if __name__ == "__main__":


    midi_to_musicxml(
        "test.mid"
    )