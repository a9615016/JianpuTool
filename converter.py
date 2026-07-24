import music21
import os


def midi_to_musicxml(input_file, output_file):

    print("MIDI -> MusicXML")

    score = music21.converter.parse(input_file)


    # 只保留主旋律
    parts = score.parts

    if len(parts) > 1:
        melody = parts[0]
    else:
        melody = score


    # 移除 pickup
    for m in melody.recurse().getElementsByClass('Measure'):
        if m.number == 0:
            m.number = 1


    # 強制 4/4
    ts = melody.recurse().getElementsByClass(
        'TimeSignature'
    )

    for t in ts:
        t.ratioString = "4/4"


    # 移除複雜元素
    for n in melody.recurse().notes:

        # 移除和弦
        if isinstance(n, music21.chord.Chord):
            p = n.pitches[0]
            n = music21.note.Note(p)


        # octave限制
        if n.pitch.octave < 3:
            n.pitch.octave = 3

        if n.pitch.octave > 6:
            n.pitch.octave = 6



    # 加入拍號
    melody.insert(
        0,
        music21.meter.TimeSignature("4/4")
    )


    # 輸出
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