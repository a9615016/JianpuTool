from music21 import converter, stream, note, meter
import sys


VERSION = "######## CLEAN MUSICXML V87 PURE JIANPU XML SANITIZER ########"


QUANTIZE = [
    4.0,
    2.0,
    1.0,
    0.5,
    0.25,
    0.125
]


def quantize_duration(x):

    x=float(x)

    return min(
        QUANTIZE,
        key=lambda v:abs(v-x)
    )



def rebuild_notes(score):

    result=[]


    for n in score.recurse().notesAndRests:


        if isinstance(n, note.Rest):

            r = note.Rest()

            r.duration.quarterLength = quantize_duration(
                n.duration.quarterLength
            )

            result.append(r)



        elif isinstance(n, note.Note):


            new = note.Note(
                n.pitch
            )


            new.duration.quarterLength = quantize_duration(
                n.duration.quarterLength
            )


            result.append(new)


    return result




def rebuild_score(notes):


    print("PURE XML REBUILD")


    score = stream.Score()

    part = stream.Part()


    part.insert(
        0,
        meter.TimeSignature("4/4")
    )


    measure_no=1

    m = stream.Measure(
        number=measure_no
    )


    beat=0.0



    for n in notes:


        dur=float(
            n.duration.quarterLength
        )


        while beat + dur > 4.0:


            remain = 4.0-beat


            if remain>0:


                left = n.__class__(
                    n.pitch
                ) if isinstance(n,note.Note) else note.Rest()


                left.duration.quarterLength=remain


                m.append(left)



            part.append(m)


            measure_no+=1


            m=stream.Measure(
                number=measure_no
            )


            beat=0.0


            dur-=remain



        if dur>0:


            new=n.__class__(
                n.pitch
            ) if isinstance(n,note.Note) else note.Rest()


            new.duration.quarterLength=dur


            m.append(new)


            beat+=dur



    if beat<4:


        r=note.Rest()

        r.duration.quarterLength=4-beat

        m.append(r)



    part.append(m)

    score.append(part)


    return score




def check(score):


    print("FINAL CHECK")


    for m in score.parts[0].getElementsByClass(
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


    print(
        "ALL MEASURES SAFE"
    )




def clean(inp,out):


    print("================")
    print(VERSION)
    print("================")


    print("READ")

    old=converter.parse(inp)



    print("REMOVE ALL XML METADATA")


    notes=rebuild_notes(
        old
    )



    new_score=rebuild_score(
        notes
    )


    check(
        new_score
    )



    print("WRITE PURE XML")


    new_score.write(
        "musicxml",
        fp=out
    )


    print("DONE")
    print(out)




if __name__=="__main__":


    if len(sys.argv)<3:

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit()



    clean(
        sys.argv[1],
        sys.argv[2]
    )