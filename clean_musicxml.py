import sys
from music21 import converter, stream, note, chord, meter
from fractions import Fraction


print("==============================")
print("CLEAN MUSICXML V33")
print("STRICT JIANPU COMPATIBLE")
print("MEASURE REBUILDER")
print("==============================")


STEP = Fraction(1, 16)
BAR = Fraction(4, 1)


# jianpu_ly 安全 duration
ALLOWED = [
    Fraction(4),
    Fraction(2),
    Fraction(1),
    Fraction(1,2),
    Fraction(1,4),
    Fraction(1,8),
    Fraction(1,16)
]


def snap_duration(x):

    x = Fraction(x)

    best=min(
        ALLOWED,
        key=lambda a:abs(a-x)
    )

    return best



def split_note(n, remain):

    new = note.Note(
        n.pitch,
        quarterLength=float(remain)
    )

    return new



def collect_notes(score):

    result=[]

    for n in score.recurse().notes:

        if isinstance(n,chord.Chord):

            n = note.Note(
                n.pitches[-1]
            )


        dur=snap_duration(
            n.duration.quarterLength
        )


        n.duration.quarterLength=float(dur)

        result.append(n)


    return result



def rebuild(notes):

    part=stream.Part()

    part.append(
        meter.TimeSignature("4/4")
    )


    measure=stream.Measure()

    pos=Fraction(0)

    number=1


    for n in notes:


        dur=Fraction(
            n.duration.quarterLength
        )


        while dur > 0:


            space=BAR-pos


            if dur <= space:

                nn=note.Note(
                    n.pitch,
                    quarterLength=float(dur)
                )

                measure.append(nn)

                pos += dur
                dur=0


            else:

                nn=split_note(
                    n,
                    space
                )

                measure.append(nn)

                dur -= space


                part.append(measure)


                print(
                    "Measure",
                    number,
                    4.0
                )

                number+=1


                measure=stream.Measure()

                pos=Fraction(0)



        if pos == BAR:

            part.append(measure)


            print(
                "Measure",
                number,
                4.0
            )


            number+=1

            measure=stream.Measure()

            pos=Fraction(0)



    # 補最後小節

    if pos>0:

        rest=note.Rest(
            quarterLength=float(
                BAR-pos
            )
        )

        measure.append(rest)

        part.append(measure)

        print(
            "Measure",
            number,
            4.0
        )


    return part



def main():

    if len(sys.argv)<3:

        print(
            "python clean_musicxml.py input output"
        )
        return


    src=sys.argv[1]
    dst=sys.argv[2]


    print("read")

    score=converter.parse(src)


    print("remove voices")
    print("remove chords")
    print("remove beams")
    print("remove ties")


    notes=collect_notes(score)


    print(
        "notes:",
        len(notes)
    )


    new_score=stream.Score()


    part=rebuild(notes)


    new_score.append(part)


    print("FINAL CHECK")


    for m in part.getElementsByClass(
        stream.Measure
    ):

        length=float(
            m.duration.quarterLength
        )

        print(
            "Measure",
            m.number,
            length
        )

        if length != 4.0:

            print(
                "ERROR BAD BAR",
                m.number
            )


    print("FINAL WRITE")


    new_score.write(
        "musicxml",
        fp=dst
    )


    print("DONE")
    print(dst)



if __name__=="__main__":
    main()