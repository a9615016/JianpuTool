# midi_to_musicxml_v3.py
# Jianpu Stable Version
# MIDI -> MusicXML -> jianpu_ly compatible

import sys
from music21 import converter, stream, note, meter, tempo, instrument
from fractions import Fraction


def quantize_duration(q):
    """
    quantize to 16th notes
    """
    steps = [
        Fraction(1,16),
        Fraction(2,16),
        Fraction(3,16),
        Fraction(4,16),
        Fraction(6,16),
        Fraction(8,16),
        Fraction(12,16),
        Fraction(16,16),
    ]

    x = Fraction(q.quarterLength).limit_denominator()

    best = min(
        steps,
        key=lambda a: abs(a-x)
    )

    return float(best)


def rebuild_melody(midi_file):

    print("讀取 MIDI...")

    src = converter.parse(midi_file)


    print("抽取旋律...")


    notes=[]

    for n in src.recurse().notes:

        if isinstance(n, note.Note):

            notes.append(n)


        elif isinstance(n, note.Chord):

            # chord 只取最高音
            top=max(n.pitches)

            nn=note.Note(top)

            nn.duration=n.duration

            nn.offset=n.offset

            notes.append(nn)



    if not notes:
        raise Exception("沒有找到音符")


    # 排序
    notes.sort(
        key=lambda x:x.offset
    )


    print("建立新 Score...")


    score=stream.Score()

    part=stream.Part()

    part.insert(
        0,
        instrument.Piano()
    )


    part.insert(
        0,
        meter.TimeSignature("4/4")
    )


    part.insert(
        0,
        tempo.MetronomeMark(number=80)
    )


    current=0.0


    print("重新量化...")


    for n in notes:


        # 填補空白 rest

        if n.offset > current:

            r=note.Rest()

            r.duration.quarterLength = quantize_duration(
                n.offset-current
            )

            part.append(r)

            current += r.duration.quarterLength



        nn=note.Note(
            n.pitch
        )


        nn.duration.quarterLength = quantize_duration(
            n.duration
        )


        part.append(nn)


        current += nn.duration.quarterLength



    score.append(part)


    print("重新建立小節...")


    # 強制 measure
    score.makeMeasures(
        inPlace=True
    )


    # 每小節檢查
    for m in score.parts[0].getElementsByClass("Measure"):

        total=sum(
            x.duration.quarterLength
            for x in m.notesAndRests
        )

        if abs(total-4.0)>0.01:

            diff=4-total

            if diff>0:

                r=note.Rest()

                r.duration.quarterLength=diff

                m.append(r)



    return score



def main():

    if len(sys.argv)<3:

        print(
            "使用方法:"
        )

        print(
            "python midi_to_musicxml_v3.py input.mid output.musicxml"
        )

        sys.exit(1)


    midi=sys.argv[1]

    output=sys.argv[2]


    print("================")
    print("MIDI → MusicXML V3")
    print("Jianpu Stable")
    print("================")


    score=rebuild_melody(
        midi
    )


    print("寫入 MusicXML...")


    score.write(
        "musicxml",
        fp=output
    )


    print()
    print("完成:")
    print(output)



if __name__=="__main__":
    main()