# CLEAN MUSICXML V26 FINAL
# Jianpu compatible
# 2026-07-28

import sys
from music21 import converter, stream, note, chord, meter, duration


def quantize_duration(q):

    allowed = [
        4.0,
        2.0,
        1.0,
        0.5,
        0.25,
        0.125
    ]

    closest = min(
        allowed,
        key=lambda x: abs(x - q)
    )

    return closest



def clean_part(part):

    new_part = stream.Part()

    ts = meter.TimeSignature("4/4")
    new_part.append(ts)

    current = 0.0

    measure_no = 1
    measure = stream.Measure(number=measure_no)

    for el in part.flatten().notesAndRests:

        if isinstance(el, chord.Chord):

            n = note.Note(
                el.pitches[0]
            )

        elif isinstance(el, note.Note):

            n = note.Note(
                el.pitch
            )

        else:
            n = note.Rest()


        d = float(el.duration.quarterLength)

        d = quantize_duration(d)


        # 超過小節直接切斷
        if current + d > 4.0:

            remain = 4.0 - current

            if remain > 0:

                n.duration = duration.Duration(
                    remain
                )

                measure.append(n)

            # 補滿
            total = sum(
                x.duration.quarterLength
                for x in measure.flatten()
            )

            if total < 4.0:

                r = note.Rest()

                r.duration = duration.Duration(
                    4.0-total
                )

                measure.append(r)


            new_part.append(measure)


            measure_no += 1

            measure = stream.Measure(
                number=measure_no
            )

            current = 0.0


            continue


        n.duration = duration.Duration(d)

        measure.append(n)

        current += d


        if abs(current-4.0) < 0.001:

            new_part.append(measure)

            measure_no += 1

            measure = stream.Measure(
                number=measure_no
            )

            current = 0.0



    # 最後一小節

    if len(measure.notesAndRests):

        total = sum(
            x.duration.quarterLength
            for x in measure.flatten()
        )

        if total < 4.0:

            r = note.Rest()

            r.duration = duration.Duration(
                4.0-total
            )

            measure.append(r)


        new_part.append(measure)



    return new_part



def check(score):

    print("FINAL CHECK")

    for m in score.parts[0].getElementsByClass(
        stream.Measure
    ):

        length = float(
            m.duration.quarterLength
        )

        print(
            "Measure",
            m.number,
            length
        )

        if abs(length-4.0) > 0.001:

            raise Exception(
                f"Measure {m.number} invalid {length}"
            )

    print("ALL MEASURES SAFE")



def main():

    if len(sys.argv)<3:

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        return


    src=sys.argv[1]
    dst=sys.argv[2]


    print("================")
    print("CLEAN MUSICXML V26 FINAL")
    print("================")


    score = converter.parse(src)


    print("remove voices")
    print("remove chords")
    print("remove beams")
    print("remove ties")


    out = stream.Score()


    for p in score.parts:

        out.append(
            clean_part(p)
        )


    check(out)


    print("FINAL WRITE")

    out.write(
        "musicxml",
        fp=dst
    )


    print("DONE")
    print(dst)



if __name__=="__main__":
    main()