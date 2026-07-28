from music21 import converter, stream, note, meter, clef
import sys


VERSION = "CLEAN MUSICXML V88 PURE JIANPU XML SANITIZER"


ALLOWED_DURATIONS = [
    4.0,
    2.0,
    1.0,
    0.5,
    0.25,
    0.125
]


def clean_duration(x):

    x = float(x)

    return min(
        ALLOWED_DURATIONS,
        key=lambda d: abs(d-x)
    )


def rebuild_from_zero(score):

    print("PURE REBUILD FROM ZERO")

    result = stream.Score()

    part = stream.Part()

    part.insert(
        0,
        meter.TimeSignature("4/4")
    )

    part.insert(
        0,
        clef.TrebleClef()
    )


    measure_no = 1

    m = stream.Measure(
        number=measure_no
    )


    beat = 0.0


    for old in score.recurse().notesAndRests:


        dur = clean_duration(
            old.duration.quarterLength
        )


        # create totally new object

        if old.isRest:

            obj = note.Rest()

        else:

            obj = note.Note(
                old.pitch
            )


        obj.duration.quarterLength = dur


        remain = dur


        while remain > 0:


            space = 4.0 - beat


            use = min(
                remain,
                space
            )


            new_obj = obj.clone()


            new_obj.duration.quarterLength = use


            m.append(
                new_obj
            )


            beat += use
            remain -= use



            if beat >= 4.0 - 0.0001:


                part.append(m)


                measure_no += 1


                m = stream.Measure(
                    number=measure_no
                )

                beat = 0.0



    # fill last bar

    if beat > 0:


        r = note.Rest()

        r.duration.quarterLength = 4-beat

        m.append(r)


        part.append(m)



    result.append(part)


    return result



def check(score):

    print("V88 FINAL CHECK")


    for m in score.parts[0].getElementsByClass(
        "Measure"
    ):


        total=sum(
            n.duration.quarterLength
            for n in m.notesAndRests
        )


        print(
            "Measure",
            m.number,
            float(total)
        )


        if abs(total-4)>0.001:

            raise Exception(
                "BAD BAR "+str(m.number)
            )


    print("V88 SAFE")



def clean(inp,out):


    print("================")
    print(VERSION)
    print("================")


    old = converter.parse(inp)


    print("remove EVERYTHING")

    new = rebuild_from_zero(old)


    check(new)


    print("WRITE XML")


    new.write(
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


    clean(
        sys.argv[1],
        sys.argv[2]
    )