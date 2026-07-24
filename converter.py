import music21
import os


def midi_to_musicxml(input_file, output_file):

    print("MIDI -> MusicXML")


    score = music21.converter.parse(input_file)


    # ==========================
    # 只取第一聲部
    # ==========================

    if len(score.parts) > 1:
        melody = score.parts[0]
    else:
        melody = score


    # ==========================
    # 移除 pickup
    # ==========================

    for m in melody.recurse().getElementsByClass(
        "Measure"
    ):

        if m.number == 0:
            m.number = 1



    # ==========================
    # 強制 4/4
    # ==========================

    melody.insert(
        0,
        music21.meter.TimeSignature("4/4")
    )



    # ==========================
    # chord -> 單音
    # ==========================

    for chord in list(
        melody.recurse().getElementsByClass(
            music21.chord.Chord
        )
    ):

        note = music21.note.Note(
            chord.pitches[0]
        )

        note.duration = chord.duration

        chord.replaceWith(note)



    # ==========================
    # octave 正規化
    # ==========================

    for note in melody.recurse().notes:

        if note.isChord:
            continue


        pitch = note.pitch


        if pitch.octave < 3:

            pitch.octave = 3


        if pitch.octave > 6:

            pitch.octave = 6


        # 重新建立 pitch
        note.pitch = music21.pitch.Pitch(
            pitch.nameWithOctave
        )



    # ==========================
    # 移除多餘 voice
    # ==========================

    for v in melody.recurse().getElementsByClass(
        music21.stream.Voice
    ):

        if len(v.notes)==0:
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