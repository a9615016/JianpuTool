# clean_musicxml.py
# V50
# jianpu_ly strict 4/4 edition
# fix real duration overflow

from music21 import converter, stream, note, meter, tempo
import sys
import copy
from fractions import Fraction


VERSION = "CLEAN MUSICXML V50"


STEP = Fraction(1,4)



def remove_bad(score):

    for n in score.recurse().notes:

        n.tie = None

        try:
            n.beams = []
        except:
            pass

        n.articulations = []
        n.expressions = []

    return score



def quantize(score):

    for x in score.recurse().notesAndRests:

        q = Fraction(x.duration.quarterLength)

        q = round(q / STEP) * STEP

        if q <= 0:
            q = STEP

        x.duration.quarterLength = q

    return score



def rebuild_strict(part):

    result = stream.Part()

    result.append(
        meter.TimeSignature("4/4")
    )


    measure_no = 1
    m = stream.Measure(number=measure_no)

    pos = Fraction(0)


    items = sorted(
        list(part.recurse().notesAndRests),
        key=lambda x:x.offset
    )


    for item in items:

        dur = Fraction(
            item.duration.quarterLength
        )


        while dur > 0:


            remain = Fraction(4)-pos


            take=min(
                dur,
                remain
            )


            new=copy.deepcopy(item)

            new.tie=None

            new.duration.quarterLength=take


            m.append(new)


            pos += take

            dur -= take



            if pos >= 4:


                result.append(m)

                measure_no += 1

                m=stream.Measure(
                    number=measure_no
                )

                pos=Fraction(0)



    # 補最後小節

    if len(m.notesAndRests):

        while pos < 4:

            r=note.Rest()

            r.duration.quarterLength=min(
                Fraction(1),
                4-pos
            )

            m.append(r)

            pos += r.duration.quarterLength


        result.append(m)


    return result



def check(score):

    print("V50 CHECK")


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


        if total != 4:

            print(
                "ERROR measure",
                i,
                total
            )



def clean(inp,out):


    print(VERSION)


    score=converter.parse(inp)


    for t in score.recurse().getElementsByClass(
        tempo.MetronomeMark
    ):
        t.activeSite.remove(t)



    remove_bad(score)

    quantize(score)



    new_score=stream.Score()



    for part in score.parts:


        new_score.append(
            rebuild_strict(part)
        )



    check(new_score)



    print("WRITE")


    new_score.write(
        "musicxml",
        fp=out
    )


    print("DONE")



if __name__=="__main__":


    inp=sys.argv[1]

    out="clean.musicxml"


    if len(sys.argv)>2:
        out=sys.argv[2]


    clean(inp,out)