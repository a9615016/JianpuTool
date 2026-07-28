from music21 import converter, stream, note, meter, duration, tempo
import sys


VERSION = "JIANPU FIX MUSICXML V3.0"


def quantize_duration(q):

    values = [
        4.0,
        2.0,
        1.0,
        0.5,
        0.25,
        0.125
    ]

    return min(values, key=lambda x: abs(x-q))


def fix_musicxml(src, dst):

    print("================")
    print(VERSION)
    print("================")

    print("READ")
    score = converter.parse(src)


    # 只保留第一個聲部
    part = score.parts[0]


    print("REMOVE VOICE")
    for el in part.recurse():
        if hasattr(el, "voice"):
            try:
                el.voice = None
            except:
                pass


    print("REMOVE CHORDS")
    notes=[]

    for n in part.recurse().notes:

        if n.isChord:
            n = n.notes[0]

        notes.append(n)


    print("REBUILD NOTES")


    new_part = stream.Part()


    # 強制 4/4

    new_part.append(
        meter.TimeSignature("4/4")
    )


    current = 0.0
    measure_no = 1

    m = stream.Measure(number=measure_no)

    m.append(
        meter.TimeSignature("4/4")
    )


    for n in notes:


        # 取得長度

        q = float(n.duration.quarterLength)


        # 修正異常長度

        if q <= 0:
            q = 0.25


        q = quantize_duration(q)


        # 如果超過小節

        if current + q > 4.0:

            remain = 4.0-current


            if remain > 0:

                r = note.Rest()

                r.duration = duration.Duration(remain)

                m.append(r)


            new_part.append(m)

            measure_no += 1

            m = stream.Measure(
                number=measure_no
            )

            current = 0



        nn = note.Note(
            n.pitch
        )


        nn.duration = duration.Duration(q)


        # 清除標記

        nn.tie = None


        m.append(nn)


        current += q



        if abs(current-4.0)<0.001:

            new_part.append(m)

            measure_no += 1

            m = stream.Measure(
                number=measure_no
            )

            current=0



    # 最後補滿

    if current > 0:

        r = note.Rest()

        r.duration = duration.Duration(
            4-current
        )

        m.append(r)

        new_part.append(m)



    print("FINAL CHECK")


    for mm in new_part.getElementsByClass(
        stream.Measure
    ):

        length = float(
            mm.duration.quarterLength
        )

        print(
            "Measure",
            mm.number,
            length
        )


    new_score = stream.Score()

    new_score.append(new_part)


    print("WRITE")

    new_score.write(
        "musicxml",
        fp=dst
    )


    print("DONE")
    print(dst)



if __name__=="__main__":


    if len(sys.argv)<3:

        print(
            "Usage:"
        )

        print(
            "python jianpu_fix_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit(1)


    fix_musicxml(
        sys.argv[1],
        sys.argv[2]
    )