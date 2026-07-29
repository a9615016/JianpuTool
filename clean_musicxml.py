# clean_musicxml.py
# V81
# jianpu_ly strict 4/4 compatible edition

from music21 import converter, stream, note, meter, tempo
import sys
import copy
from fractions import Fraction


VERSION = "CLEAN MUSICXML V81"


STEP_VALUES = [
    Fraction(1,4),
    Fraction(1,2),
    Fraction(1),
    Fraction(2),
    Fraction(4)
]


def remove_notation(score):

    for n in score.recurse().notesAndRests:

        if hasattr(n, "tie"):
            n.tie = None

        if hasattr(n, "beams"):
            n.beams = []

        if hasattr(n, "articulations"):
            n.articulations = []

        if hasattr(n, "expressions"):
            n.expressions = []

    return score



def remove_tempo(score):

    for t in list(
        score.recurse().getElementsByClass(
            tempo.MetronomeMark
        )
    ):
        t.activeSite.remove(t)

    return score



def force_44(score):

    for part in score.parts:

        part.insert(
            0,
            meter.TimeSignature("4/4")
        )

    return score



def quantize_exact(part):

    for n in part.recurse().notesAndRests:

        q = Fraction(
            n.duration.quarterLength
        )

        closest = min(
            STEP_VALUES,
            key=lambda x: abs(x-q)
        )

        n.duration.quarterLength = closest

    return part



def rebuild_measure(part):

    new_part = stream.Part()

    new_part.append(
        meter.TimeSignature("4/4")
    )

    measure = stream.Measure(
        number=1
    )

    pos = Fraction(0)


    for item in part.recurse().notesAndRests:


        dur = Fraction(
            item.duration.quarterLength
        )


        while dur > 0:


            remain = Fraction(4) - pos

            take = min(
                dur,
                remain
            )


            new = copy.deepcopy(item)

            new.tie = None

            new.duration.quarterLength = take


            measure.append(new)


            pos += take
            dur -= take


            if pos == 4:

                new_part.append(measure)

                measure = stream.Measure(
                    number=len(
                        new_part.getElementsByClass(
                            stream.Measure
                        )
                    ) + 1
                )

                pos = Fraction(0)



    # 補最後小節

    if len(measure.notesAndRests):

        while pos < 4:

            r = note.Rest()

            r.duration.quarterLength = min(
                Fraction(1),
                4-pos
            )

            measure.append(r)

            pos += r.duration.quarterLength


        new_part.append(measure)


    return new_part




def strict_measure_fix(score):

    for part in score.parts:

        for m in part.getElementsByClass(
            stream.Measure
        ):

            total = sum(
                Fraction(x.duration.quarterLength)
                for x in m.notesAndRests
            )


            if total != 4:

                diff = Fraction(4)-total


                if diff > 0:

                    r = note.Rest()

                    r.duration.quarterLength = diff

                    m.append(r)


    return score




def final_check(score):

    print("V81 FINAL CHECK")


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


        if total != 4:

            print(
                "BAD MEASURE",
                i,
                total
            )




def clean(inp,out):

    print(VERSION)


    score = converter.parse(inp)


    score = remove_tempo(score)

    score = remove_notation(score)


    new_score = stream.Score()



    for part in score.parts:


        quantize_exact(part)


        np = rebuild_measure(part)


        new_score.append(np)



    force_44(new_score)


    new_score = strict_measure_fix(
        new_score
    )


    final_check(
        new_score
    )


    print(
        "FINAL WRITE"
    )


    new_score.write(
        "musicxml",
        fp=out
    )


    print(
        "DONE",
        out
    )




if __name__=="__main__":


    inp=sys.argv[1]


    out="clean.musicxml"


    if len(sys.argv)>2:

        out=sys.argv[2]


    clean(
        inp,
        out
    )