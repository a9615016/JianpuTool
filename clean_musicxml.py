# clean_musicxml.py
# V40
# jianpu_ly hard compatible edition

from music21 import converter, stream, note, chord, meter, tempo
import sys
import copy
from fractions import Fraction


VERSION = "CLEAN MUSICXML V40"


STEP = Fraction(1,4)   # 16th note


def remove_notation(score):

    for n in score.recurse().notes:

        # remove tie
        n.tie = None

        # remove beams
        if hasattr(n,"beams"):
            n.beams = []

        # remove articulations
        n.articulations = []

        # remove expressions
        n.expressions = []

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

    for n in part.recurse().notesAndRests:

        q = Fraction(
            n.duration.quarterLength
        )

        new = round(q/STEP)*STEP

        if new <=0:
            new = STEP

        n.duration.quarterLength = new

    return part



def rebuild_part(part):

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


        while dur>0:


            remain = 4-pos


            take=min(
                dur,
                remain
            )


            new = copy.deepcopy(item)

            new.tie=None

            new.duration.quarterLength = take


            measure.append(new)


            pos += take

            dur -= take



            if pos>=4:

                new_part.append(measure)

                measure=stream.Measure(
                    number=len(new_part.getElementsByClass(stream.Measure))+1
                )

                pos=0



    # 補滿最後小節

    while pos<4:

        r=note.Rest()

        r.duration.quarterLength=min(
            1,
            4-pos
        )

        measure.append(r)

        pos += r.duration.quarterLength


    new_part.append(measure)


    return new_part



def final_check(score):

    print("V40 FINAL CHECK")

    for i,m in enumerate(
        score.parts[0].getElementsByClass(stream.Measure),
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


    score=converter.parse(inp)


    # remove tempo
    for t in score.recurse().getElementsByClass(
        tempo.MetronomeMark
    ):
        t.activeSite.remove(t)


    score=remove_notation(score)

    score=force_44(score)


    new_score=stream.Score()


    for part in score.parts:

        quantize(part)

        np=rebuild_part(part)

        new_score.append(np)



    force_44(new_score)


    final_check(new_score)


    print("FINAL WRITE")


    new_score.write(
        "musicxml",
        fp=out
    )


    print("DONE")
    print(out)



if __name__=="__main__":


    inp=sys.argv[1]


    out="clean.musicxml"

    if len(sys.argv)>2:
        out=sys.argv[2]


    clean(inp,out)