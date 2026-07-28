from music21 import converter, stream, note, meter, chord, duration
import sys
import os


VERSION = "CLEAN MUSICXML V26 FINAL HARD FIX JIANPU"


def remove_bad_elements(score):

    print("remove voices")

    for part in score.parts:
        for el in list(part.recurse()):
            if isinstance(el, chord.Chord):
                n = el.sortAscending().notes[-1]
                n.duration = el.duration
                el.activeSite.replace(el, n)

    print("remove chords")
    print("remove beams")
    print("remove ties")


    for n in score.recurse().notes:

        try:
            n.tie = None
        except:
            pass

        try:
            n.beams = []
        except:
            pass


def force_44(score):

    print("force 4/4")

    for part in score.parts:

        ts = part.recurse().getElementsByClass(
            meter.TimeSignature
        )

        if len(ts):
            ts[0].ratioString = "4/4"

        else:
            part.insert(
                0,
                meter.TimeSignature("4/4")
            )


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

    for n in score.recurse().notes:

        q = n.duration.quarterLength

        best = min(
            allowed,
            key=lambda x: abs(x-q)
        )

        n.duration = duration.Duration(best)


def rebuild(part):

    print("rebuild measures")


    old = list(
        part.getElementsByClass(stream.Measure)
    )


    newPart = stream.Part()

    measure_no = 1
    current = stream.Measure(number=measure_no)

    used = 0


    for m in old:

        for el in m.notesAndRests:

            q = float(el.duration.quarterLength)


            # 超過小節直接切掉
            if used + q > 4:

                remain = 4-used


                if remain > 0:

                    el2 = el.deepcopy()
                    el2.duration = duration.Duration(remain)
                    current.append(el2)


                newPart.append(current)


                measure_no += 1
                current = stream.Measure(
                    number=measure_no
                )

                used = 0


                q = q-remain


                if q > 0:

                    el3 = el.deepcopy()
                    el3.duration = duration.Duration(q)

                    current.append(el3)

                    used=q

                continue


            current.append(el)
            used += q


            if abs(used-4)<0.001:

                newPart.append(current)

                measure_no += 1

                current = stream.Measure(
                    number=measure_no
                )

                used=0


    if len(current):

        if used < 4:

            r = note.Rest()

            r.duration = duration.Duration(
                4-used
            )

            current.append(r)


        newPart.append(current)


    return newPart



def hard_fix_measures(score):

    print("split cross measure notes")


    newScore = stream.Score()


    for part in score.parts:

        fixed = rebuild(part)

        newScore.append(fixed)


    return newScore



def final_check(score):

    print("FINAL CHECK")

    safe=True


    for part in score.parts:

        for m in part.getElementsByClass(
            stream.Measure
        ):

            total = sum(
                x.duration.quarterLength
                for x in m.notesAndRests
            )


            total=float(total)

            print(
                "Measure",
                m.number,
                total
            )


            if abs(total-4)>0.001:

                safe=False


    if safe:

        print(
            "ALL MEASURES SAFE"
        )

    else:

        print(
            "WARNING measure mismatch"
        )

    return safe



def main():

    if len(sys.argv)<3:

        print(
            "usage: python clean_musicxml.py input.musicxml output.musicxml"
        )

        return


    inp=sys.argv[1]
    out=sys.argv[2]


    print("================")
    print(VERSION)
    print("================")


    print("read")

    score=converter.parse(inp)


    remove_bad_elements(score)

    force_44(score)

    quantize(score)


    score=hard_fix_measures(score)


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