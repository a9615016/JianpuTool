from music21 import converter, note, meter
import sys
import copy


print("================")
print("CLEAN MUSICXML V28 JIANPU HARD SPLIT FIX")
print("================")


def remove_chords(score):

    print("remove chords")

    for part in score.parts:

        for c in list(
            part.recurse().getElementsByClass("Chord")
        ):

            n = note.Note(c.root())

            n.duration = c.duration

            c.activeSite.replace(c,n)



def remove_ties(score):

    print("remove ties")

    for n in score.recurse().notes:

        n.tie=None



def quantize_duration(score):

    print("duration quantize")

    allowed=[
        4,
        2,
        1,
        0.5,
        0.25
    ]


    for n in score.recurse().notesAndRests:

        q=n.duration.quarterLength

        best=min(
            allowed,
            key=lambda x:abs(x-q)
        )

        n.duration.quarterLength=best



def force_44(score):

    print("force 4/4")

    for p in score.parts:

        p.insert(
            0,
            meter.TimeSignature("4/4")
        )



def split_cross_measure_notes(score):

    print("split cross measure notes HARD")


    for part in score.parts:


        measures=list(
            part.getElementsByClass("Measure")
        )


        carry=[]


        for m in measures:


            current=[]


            for n in list(m.notesAndRests):


                start=n.offset

                dur=n.duration.quarterLength

                end=start+dur



                if end>4:


                    first=4-start

                    remain=end-4



                    if first>0:

                        n1=copy.deepcopy(n)

                        n1.duration.quarterLength=first

                        n1.tie=None


                        current.append(
                            (start,n1)
                        )


                    if remain>0:

                        n2=copy.deepcopy(n)

                        n2.offset=0

                        n2.duration.quarterLength=remain

                        n2.tie=None


                        carry.append(n2)



                else:


                    n.tie=None


                    current.append(
                        (start,n)
                    )



            # 清空原 Measure

            for old in list(m.notesAndRests):

                m.remove(old)



            # 放回修正後音符

            for offset,n in current:

                m.insert(
                    offset,
                    n
                )



            # 加入下一小節剩餘音

            if carry:

                for n in carry:

                    m.insert(
                        0,
                        n
                    )

                carry=[]




def rebuild_measures(score):

    print("rebuild measures")


    for part in score.parts:


        for m in part.getElementsByClass("Measure"):


            total=sum(
                x.duration.quarterLength
                for x in m.notesAndRests
            )


            print(
                "Measure",
                m.number,
                total
            )


            if total<4:


                r=note.Rest()

                r.duration.quarterLength=4-total

                m.append(r)



def final_check(score):

    print("FINAL CHECK")


    ok=True


    for part in score.parts:


        for m in part.getElementsByClass("Measure"):


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

                ok=False



    if ok:

        print("ALL MEASURES SAFE")

    else:

        print("WARNING measure mismatch")




def main():

    inp=sys.argv[1]

    out=sys.argv[2]


    print("read")


    score=converter.parse(inp)


    print("remove voices")

    print("remove beams")


    remove_chords(score)

    remove_ties(score)


    force_44(score)


    quantize_duration(score)


    split_cross_measure_notes(score)


    rebuild_measures(score)


    remove_ties(score)


    print("clear notation cache")


    final_check(score)


    print("FINAL WRITE")


    score.write(
        "musicxml",
        fp=out
    )


    print("DONE")

    print(out)



if __name__=="__main__":

    main()