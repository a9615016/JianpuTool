# ==========================================
# jianpu_fix_musicxml.py V3.0
# Jianpu_ly compatibility fixer
# ==========================================

import sys
from music21 import converter, stream, note, meter, duration


ALLOWED_DURATIONS = [
    4.0,
    2.0,
    1.0,
    0.5,
    0.25,
    0.125
]


def quantize_duration(q):

    closest = min(
        ALLOWED_DURATIONS,
        key=lambda x: abs(x - q)
    )

    return closest


def clean_note(n):

    if isinstance(n, note.Note):

        q = float(n.duration.quarterLength)

        q = quantize_duration(q)

        n.duration = duration.Duration(q)

        if n.tie:
            n.tie = None


    elif isinstance(n, note.Rest):

        q = float(n.duration.quarterLength)

        q = quantize_duration(q)

        n.duration = duration.Duration(q)


    return n



def rebuild_measure(measure):

    fixed = stream.Measure(
        number=measure.number
    )

    used = 0.0


    for n in measure.notesAndRests:

        n = clean_note(n)

        q = float(n.duration.quarterLength)


        # 超過4拍停止
        if used + q > 4:

            remain = 4 - used

            if remain > 0:

                r = note.Rest(
                    quarterLength=remain
                )

                fixed.append(r)

                used += remain

            break


        fixed.append(n)

        used += q



    # 不足補休止

    if used < 4:

        r = note.Rest(
            quarterLength=4-used
        )

        fixed.append(r)

        used = 4



    print(
        "FIX Measure",
        measure.number,
        used
    )


    return fixed



def fix_score(score):

    print("================")
    print("JIANPU FIX MUSICXML V3.0")
    print("================")


    score.removeByClass('Chord')


    for part in score.parts:


        new_part = stream.Part()

        new_part.insert(
            0,
            meter.TimeSignature("4/4")
        )


        for m in part.getElementsByClass(
            stream.Measure
        ):

            new_m = rebuild_measure(m)

            new_part.append(new_m)



        part.replace(
            part,
            new_part
        )



    return score



def main():

    if len(sys.argv) < 3:

        print(
            "usage: python jianpu_fix_musicxml.py input.musicxml output.musicxml"
        )

        return



    inp = sys.argv[1]
    out = sys.argv[2]


    print("READ")
    score = converter.parse(inp)


    score = fix_score(score)



    print("FINAL CHECK")


    for p in score.parts:

        for m in p.getElementsByClass(
            stream.Measure
        ):

            total = sum(
                float(x.duration.quarterLength)
                for x in m.notesAndRests
            )


            print(
                "Measure",
                m.number,
                total
            )



    print("WRITE")

    score.write(
        "musicxml",
        fp=out
    )


    print("DONE")
    print(out)



if __name__ == "__main__":
    main()