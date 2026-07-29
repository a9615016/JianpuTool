# clean_musicxml.py V40
# Jianpu_ly dedicated edition

import sys
import music21
from music21 import converter, stream, note, chord, meter, bar

print("CLEAN MUSICXML V40")
print("jianpu_ly compatibility mode")


def clean_score(src, out):

    score = converter.parse(src)

    print("remove ties")
    for n in score.recurse().notes:
        n.tie = None


    print("remove beams")
    for n in score.recurse().notes:
        try:
            n.beams = None
        except:
            pass


    print("remove grace")
    for n in score.recurse().notes:
        if hasattr(n, "duration"):
            n.duration = n.duration.getQuarterLength()


    # force 4/4
    print("force 4/4")

    for p in score.parts:
        p.insert(0, meter.TimeSignature("4/4"))


    print("quantize durations")

    allowed = [
        0.25,
        0.5,
        1,
        2,
        4
    ]

    for n in score.recurse().notes:

        q=n.duration.quarterLength

        closest=min(
            allowed,
            key=lambda x:abs(x-q)
        )

        n.duration.quarterLength=closest



    print("rebuild measures")

    for p in score.parts:

        p.makeMeasures(
            inPlace=True
        )


        for m in p.getElementsByClass(
            stream.Measure
        ):

            total=0

            for n in m.notesAndRests:

                total+=n.duration.quarterLength


            print(
                "Measure",
                m.number,
                total
            )


            # 超過4拍
            if total>4:

                print(
                    "fix overflow measure",
                    m.number,
                    total
                )


                remain=4

                new=[]


                for n in m.notesAndRests:

                    if remain<=0:
                        break

                    dur=min(
                        n.duration.quarterLength,
                        remain
                    )

                    n.duration.quarterLength=dur

                    new.append(n)

                    remain-=dur


                if remain>0:

                    r=note.Rest()
                    r.duration.quarterLength=remain
                    new.append(r)


                m.notesAndRests[:] = new



    print("FINAL CHECK")


    for p in score.parts:
        for m in p.getElementsByClass(stream.Measure):

            total=sum(
                n.duration.quarterLength
                for n in m.notesAndRests
            )

            print(
                "Measure",
                m.number,
                total
            )


    score.write(
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
        exit()


    clean_score(
        sys.argv[1],
        sys.argv[2]
    )