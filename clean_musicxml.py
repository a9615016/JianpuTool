# clean_musicxml.py
# V41
# jianpu_ly strict 4/4 edition

from music21 import converter, stream, note, chord, meter, tempo
import sys
import copy
from fractions import Fraction


VERSION = "CLEAN MUSICXML V41"


STEP = Fraction(1, 4)


def clean_note(n):

    n.tie = None

    if hasattr(n, "beams"):
        n.beams = []

    n.articulations = []
    n.expressions = []

    return n



def remove_bad_elements(score):

    print("clear notation cache")

    for n in score.recurse().notes:

        clean_note(n)

    return score



def force_44(score):

    for part in score.parts:

        for ts in part.recurse().getElementsByClass(
            meter.TimeSignature
        ):
            ts.numerator = 4
            ts.denominator = 4

    return score



def quantize(part):

    print("duration quantize")

    for n in part.recurse().notes:

        q = Fraction(
            n.duration.quarterLength
        )

        new_q = round(q / STEP) * STEP

        if new_q <= 0:
            new_q = STEP

        n.duration.quarterLength = new_q



def expand_chords(part):

    result=[]

    for n in part.recurse().notes:

        if isinstance(n, chord.Chord):

            # 取最高音當旋律
            result.append(
                n.notes[-1]
            )

        else:

            result.append(n)

    return result



def rebuild_measure(part):

    print("rebuild measures")

    new_part = stream.Part()

    new_part.insert(
        0,
        meter.TimeSignature("4/4")
    )


    measure_no = 1

    m = stream.Measure(
        number=measure_no
    )


    pos = Fraction(0)


    notes = expand_chords(part)


    for old in notes:


        dur = Fraction(
            old.duration.quarterLength
        )


        while dur > 0:


            remain = Fraction(4)-pos


            take=min(
                dur,
                remain
            )


            new = copy.deepcopy(old)


            clean_note(new)


            new.duration.quarterLength = take


            # 強制重新 offset

            m.insert(
                pos,
                new
            )


            pos += take

            dur -= take



            if pos >= 4:


                new_part.append(m)


                measure_no += 1

                m = stream.Measure(
                    number=measure_no
                )

                pos = Fraction(0)



    # 最後補滿小節

    while pos < 4:


        r = note.Rest()


        r.duration.quarterLength = min(
            STEP,
            Fraction(4)-pos
        )


        m.insert(
            pos,
            r
        )


        pos += r.duration.quarterLength



    if len(m.notesAndRests):

        new_part.append(m)


    return new_part



def final_check(score):

    print("FINAL CHECK")

    for i,m in enumerate(
        score.parts[0]
        .getElementsByClass(stream.Measure),
        1
    ):

        total=sum(
            Fraction(x.duration.quarterLength)
            for x in m.notesAndRests
        )


        print(
            "Measure",
            i,
            float(total)
        )



def clean(inp,out):


    print(VERSION)


    score = converter.parse(inp)


    # remove tempo

    for t in score.recurse().getElementsByClass(
        tempo.MetronomeMark
    ):

        t.activeSite.remove(t)



    score = remove_bad_elements(score)


    force_44(score)



    new_score = stream.Score()


    for part in score.parts:


        quantize(part)


        rebuilt = rebuild_measure(part)


        new_score.append(
            rebuilt
        )



    force_44(new_score)



    final_check(
        new_score
    )


    print("FINAL WRITE")


    new_score.write(
        "musicxml",
        fp=out
    )


    print("DONE")
    print(out)



if __name__ == "__main__":


    if len(sys.argv)<2:

        print(
            "usage: python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit()


    inp=sys.argv[1]


    out="clean.musicxml"


    if len(sys.argv)>=3:

        out=sys.argv[2]


    clean(
        inp,
        out
    )