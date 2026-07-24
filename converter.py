import os
import sys
import music21


def midi_to_musicxml(input_file):

    print("開始 MIDI → MusicXML")


    folder=os.path.dirname(input_file)


    output_file=os.path.join(
        folder,
        "input.musicxml"
    )


    score=music21.converter.parse(
        input_file
    )


    print("量化")


    score.quantize(
        quarterLengthDivisors=[
            4,
            8,
            16
        ]
    )



    print("建立小節")


    # 強制 4/4

    score.insert(
        0,
        music21.meter.TimeSignature("4/4")
    )



    # 移除多餘譜表

    score=score.flatten()



    score.write(
        "musicxml",
        fp=output_file
    )



    print(
        "MusicXML完成"
    )

    print(output_file)



    return output_file





if __name__=="__main__":


    midi=sys.argv[1]


    midi_to_musicxml(
        midi
    )