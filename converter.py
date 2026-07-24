import music21
import sys


def midi_to_musicxml(input_file, output_file):

    print("MIDI -> MusicXML")


    score = music21.converter.parse(input_file)



    # 只取第一旋律
    if len(score.parts) > 0:
        melody = score.parts[0]
    else:
        melody = score



    # ----------------------
    # Quantize 音符
    # ----------------------

    melody.quantize(
        quarterLengthDivisors=[
            4,
            3,
            2,
            1
        ],
        processOffsets=True,
        processDurations=True
    )



    # ----------------------
    # 修正 duration
    # ----------------------

    for n in melody.recurse().notes:

        if n.duration.quarterLength <= 0:

            n.duration.quarterLength = 1


        # 限制太長/太短
        if n.duration.quarterLength > 8:

            n.duration.quarterLength = 8



        # octave限制

        if n.pitch.octave < 3:
            n.pitch.octave = 3


        if n.pitch.octave > 6:
            n.pitch.octave = 6




    # ----------------------
    # 加 4/4
    # ----------------------

    melody.insert(
        0,
        music21.meter.TimeSignature("4/4")
    )



    melody.write(
        "musicxml",
        fp=output_file
    )


    print(
        "完成:",
        output_file
    )



if __name__=="__main__":

    midi_to_musicxml(
        sys.argv[1],
        sys.argv[2]
    )