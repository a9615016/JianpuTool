# midi_to_musicxml_v2.py
# Jianpu friendly MIDI -> MusicXML

import sys
from music21 import converter, stream, note, meter, tempo


def quantize_duration(q):
    """
    簡譜友善時值
    """
    allowed = [
        4.0,   # 全音符
        2.0,   # 二分
        1.0,   # 四分
        0.5,   # 八分
        0.25,  # 十六分
    ]

    return min(
        allowed,
        key=lambda x: abs(x-q)
    )


def rebuild(score):

    new_score = stream.Score()
    part = stream.Part()

    part.append(meter.TimeSignature("4/4"))

    # tempo
    part.append(
        tempo.MetronomeMark(number=80)
    )


    current = 0

    for n in score.flat.notes:

        if isinstance(n, note.Rest):
            continue

        # 只取單音
        if isinstance(n, note.Note):

            dur = quantize_duration(
                float(n.duration.quarterLength)
            )

            new_note = note.Note(
                n.pitch
            )

            new_note.duration.quarterLength = dur


            # 防止跨小節
            pos = current % 4

            if pos + dur > 4:

                rest = note.Rest()

                rest.duration.quarterLength = (
                    4-pos
                )

                part.append(rest)

                current += (4-pos)


            part.append(new_note)

            current += dur


    # 補滿最後小節

    remain = 4 - (current % 4)

    if remain < 4:
        r = note.Rest()
        r.duration.quarterLength = remain
        part.append(r)


    new_score.append(part)

    return new_score



def main():

    if len(sys.argv)<3:
        print(
            "usage: python midi_to_musicxml_v2.py input.mid output.musicxml"
        )
        return


    inp=sys.argv[1]
    out=sys.argv[2]


    print("================")
    print("MIDI TO MUSICXML V2")
    print("JIANPU FRIENDLY")
    print("================")


    print("read midi")

    score = converter.parse(inp)


    print("rebuild melody")

    new_score = rebuild(score)


    print("write musicxml")

    new_score.write(
        "musicxml",
        fp=out
    )


    print("DONE")
    print(out)



if __name__=="__main__":
    main()