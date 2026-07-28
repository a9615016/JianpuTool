from music21 import converter, stream, note, meter
import sys
import copy
import math


print("==============================")
print("CLEAN MUSICXML V30 TIMELINE REBUILD")
print("==============================")


def remove_chords(score):
    print("remove chords")

    for c in list(score.recurse().getElementsByClass("Chord")):
        n = note.Note(c.root())
        n.duration = c.duration
        c.activeSite.replace(c, n)



def remove_ties(score):
    print("remove ties")

    for n in score.recurse().notes:
        n.tie = None



def quantize(score):

    print("duration quantize")

    allowed = [
        4,
        2,
        1,
        0.5,
        0.25,
        0.125
    ]

    for n in score.recurse().notesAndRests:

        q = n.duration.quarterLength

        best = min(
            allowed,
            key=lambda x:abs(x-q)
        )

        n.duration.quarterLength = best



def rebuild_timeline(score):

    print("REBUILD TIMELINE MEASURES")


    part_out = stream.Part()


    part_out.insert(
        0,
        meter.TimeSignature("4/4")
    )


    notes=[]


    for n in score.flatten().notesAndRests:

        notes.append(
            copy.deepcopy(n)
        )


    notes.sort(
        key=lambda x:x.offset
    )


    measure_no=1

    current_measure = stream.Measure(
        number=measure_no
    )


    measure_start=0


    for n in notes:


        start=n.offset

        dur=n.duration.quarterLength


        while start >= measure_start+4:

            fill_rest(
                current_measure
            )

            part_out.append(
                current_measure
            )

            measure_no += 1

            current_measure=stream.Measure(
                number=measure_no
            )

            measure_start += 4



        local_pos=start-measure_start


        remain=dur


        while remain>0:


            available=4-local_pos


            take=min(
                remain,
                available
            )


            nn=copy.deepcopy(n)

            nn.duration.quarterLength=take

            nn.tie=None


            current_measure.insert(
                local_pos,
                nn
            )


            remain-=take


            if remain>0:

                fill_rest(
                    current_measure
                )

                part_out.append(
                    current_measure
                )


                measure_no+=1

                current_measure=stream.Measure(
                    number=measure_no
                )

                measure_start+=4

                local_pos=0

            else:

                local_pos+=take



    fill_rest(
        current_measure
    )


    part_out.append(
        current_measure
    )


    return part_out



def fill_rest(m):

    total=sum(
        x.duration.quarterLength
        for x in m.notesAndRests
    )


    if total < 4:

        r=note.Rest()

        r.duration.quarterLength=4-total

        m.append(r)



def final_check(score):

    print("FINAL CHECK")

    ok=True


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

            ok=False


    if ok:

        print("ALL MEASURES SAFE")

    else:

        print("FAILED")



def main():

    inp=sys.argv[1]
    out=sys.argv[2]


    print("read")

    score=converter.parse(inp)


    print("remove beams")

    remove_chords(score)

    remove_ties(score)

    quantize(score)


    new_part=rebuild_timeline(score)


    new_score=stream.Score()

    new_score.append(
        new_part
    )


    remove_ties(new_score)


    print("clear notation cache")


    final_check(new_score)


    print("FINAL WRITE")


    new_score.write(
        "musicxml",
        fp=out
    )


    print("DONE")
    print(out)



if __name__=="__main__":
    main()