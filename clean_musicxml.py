from music21 import converter, stream, note, meter
import copy
import sys


VERSION="######## USING V84 HARD QUANTIZE CLEANER ########"


GRID=[
    4.0,
    2.0,
    1.0,
    0.5,
    0.25
]


def qdur(x):

    return min(
        GRID,
        key=lambda y:abs(y-x)
    )


def clean_notes(score):

    result=[]

    for n in score.recurse().notesAndRests:

        x=copy.deepcopy(n)


        if hasattr(x,"expressions"):
            x.expressions=[]

        if hasattr(x,"lyrics"):
            x.lyrics=[]


        x.duration.quarterLength=qdur(
            float(x.duration.quarterLength)
        )


        result.append(x)


    return result



def rebuild(notes):

    print("V84 rebuild")

    s=stream.Score()

    p=stream.Part()

    p.append(
        meter.TimeSignature("4/4")
    )


    m=stream.Measure(1)

    beat=0
    num=1


    for n in notes:

        dur=float(
            n.duration.quarterLength
        )


        while dur>0:


            remain=4-beat


            take=min(
                dur,
                remain
            )


            nn=copy.deepcopy(n)

            nn.duration.quarterLength=take


            m.append(nn)

            beat+=take
            dur-=take



            if beat>=4-0.0001:

                p.append(m)

                num+=1

                m=stream.Measure(num)

                beat=0



    if beat>0:

        r=note.Rest()

        r.duration.quarterLength=4-beat

        m.append(r)

        p.append(m)



    s.append(p)


    return s



def check(s):

    print("V84 CHECK")


    for m in s.parts[0].getElementsByClass(
        "Measure"
    ):

        total=sum(
            float(x.duration.quarterLength)
            for x in m.notesAndRests
        )

        print(
            "Measure",
            m.number,
            total
        )


        if abs(total-4)>0.001:

            raise Exception(
                "BAD "+str(m.number)
            )


    print("V84 SAFE")



def run(inp,out):

    print(VERSION)

    old=converter.parse(inp)


    notes=clean_notes(old)


    new=rebuild(notes)


    check(new)


    new.write(
        "musicxml",
        fp=out
    )


    print("DONE",out)



if __name__=="__main__":

    run(
        sys.argv[1],
        sys.argv[2]
    )