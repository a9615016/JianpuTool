from music21 import converter, stream, note, meter, clef
import sys


VERSION="CLEAN MUSICXML V91 HARD RESET"


DURS=[
    4.0,
    2.0,
    1.0,
    0.5,
    0.25,
    0.125
]


def quantize(d):

    return min(
        DURS,
        key=lambda x:abs(x-d)
    )



def rebuild(score):

    print(VERSION)

    out=stream.Score()

    part=stream.Part()


    part.insert(
        0,
        meter.TimeSignature("4/4")
    )

    part.insert(
        0,
        clef.TrebleClef()
    )


    measure=stream.Measure(
        number=1
    )


    beat=0


    for n in score.recurse().notesAndRests:


        dur=quantize(
            float(n.duration.quarterLength)
        )


        if n.isRest:

            new=note.Rest()

        else:

            new=note.Note(
                n.pitch
            )


        # HARD RESET

        new.duration.quarterLength=dur


        remain=dur


        while remain>0:


            space=4-beat


            use=min(
                remain,
                space
            )


            if new.isRest:

                x=note.Rest()

            else:

                x=note.Note(
                    new.pitch
                )


            x.duration.quarterLength=use


            measure.append(x)


            beat+=use
            remain-=use



            if beat>=3.999:


                part.append(measure)


                measure=stream.Measure(
                    number=len(part.getElementsByClass("Measure"))+1
                )

                beat=0



    if beat>0:

        r=note.Rest()

        r.duration.quarterLength=4-beat

        measure.append(r)

        part.append(measure)



    out.append(part)


    return out



def check(score):

    print("V91 FINAL CHECK")


    for m in score.parts[0].getElementsByClass("Measure"):

        total=sum(
            x.duration.quarterLength
            for x in m.notesAndRests
        )

        print(
            "Measure",
            m.number,
            total
        )


        if abs(total-4)>0.001:

            raise Exception(
                "BAD BAR "+str(m.number)
            )


    print("SAFE")




def clean(inp,out):


    old=converter.parse(inp)


    new=rebuild(old)


    check(new)


    new.write(
        "musicxml",
        fp=out
    )


    print("DONE",out)



if __name__=="__main__":


    clean(
        sys.argv[1],
        sys.argv[2]
    )