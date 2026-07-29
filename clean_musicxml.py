# clean_musicxml.py
# V51
# jianpu_ly hard compatible
# force measure-level 4/4

from music21 import converter, stream, note, meter, tempo
import sys
import copy
from fractions import Fraction


VERSION="CLEAN MUSICXML V51"


STEP=Fraction(1,4)



def remove_all_time_signature(score):

    for part in score.parts:

        for ts in list(
            part.recurse()
            .getElementsByClass(meter.TimeSignature)
        ):
            ts.activeSite.remove(ts)

    return score



def quantize(part):

    for n in part.recurse().notesAndRests:

        q=Fraction(n.duration.quarterLength)

        new=round(q/STEP)*STEP

        if new<=0:
            new=STEP

        n.duration.quarterLength=new


    return part



def rebuild(part):

    new_part=stream.Part()


    measure_no=1
    measure=stream.Measure(number=measure_no)

    measure.insert(
        0,
        meter.TimeSignature("4/4")
    )


    pos=Fraction(0)


    for item in part.recurse().notesAndRests:

        dur=Fraction(item.duration.quarterLength)


        while dur>0:

            remain=Fraction(4)-pos

            take=min(dur,remain)


            new=copy.deepcopy(item)

            new.duration.quarterLength=take

            new.tie=None


            measure.append(new)


            pos+=take
            dur-=take



            if pos>=4:

                new_part.append(measure)

                measure_no+=1

                measure=stream.Measure(
                    number=measure_no
                )

                measure.insert(
                    0,
                    meter.TimeSignature("4/4")
                )

                pos=Fraction(0)



    if len(measure.notesAndRests):

        while pos<4:

            r=note.Rest()

            r.duration.quarterLength=min(
                1,
                4-pos
            )

            measure.append(r)

            pos+=r.duration.quarterLength


        new_part.append(measure)



    return new_part




def check(score):

    print("V51 FINAL CHECK")


    for i,m in enumerate(
        score.parts[0]
        .getElementsByClass(stream.Measure),
        1
    ):

        ts=m.timeSignature

        if ts:

            print(
                "Measure",
                i,
                "TS",
                ts.ratioString
            )


        total=sum(
            Fraction(x.duration.quarterLength)
            for x in m.notesAndRests
        )


        print(
            "Length",
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



    score=remove_all_time_signature(score)



    new_score=stream.Score()



    for part in score.parts:

        quantize(part)

        new_score.append(
            rebuild(part)
        )



    check(new_score)



    print("WRITE")


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