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


    score=music21.converter.parse(input_file)


    print("保留第一聲部")

    parts=score.parts

    if len(parts)>0:
        score=parts[0]


    print("量化")

    score.quantize(
        quarterLengthDivisors=[4,8,16]
    )


    print("強制4/4")


    # 清除舊拍號
    for ts in score.recurse().getElementsByClass(
        music21.meter.TimeSignature
    ):
        ts.ratioString="4/4"


    if len(
        score.recurse().getElementsByClass(
            music21.meter.TimeSignature
        )
    )==0:

        score.insert(
            0,
            music21.meter.TimeSignature("4/4")
        )



    print("建立小節")


    score.makeMeasures(
        inPlace=True
    )


    print("修正小節")


    for m in score.recurse().getElementsByClass(
        music21.stream.Measure
    ):

        m.timeSignature = music21.meter.TimeSignature("4/4")



    print("輸出")


    score.write(
        "musicxml",
        fp=output_file
    )


    print(output_file)


    return output_file



if __name__=="__main__":

    midi=sys.argv[1]

    midi_to_musicxml(midi)