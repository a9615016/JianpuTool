from music21 import converter, stream, note, meter, clef
import sys


VERSION = "CLEAN MUSICXML V89 PURE JIANPU FORCE 4/4"


# 16分音符以下不保留
GRID = 0.25


def clean_duration(x):

    x = float(x)

    q = round(x / GRID) * GRID

    if q <= 0:
        q = GRID

    return q



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


        remain = dur


        while remain > 0:


            space = 4.0 - beat


            use = min(
                remain,
                space
            )


            # create fresh object
            if old.isRest:

                new_obj = note.Rest()

            else:

                new_obj = note.Note(
                    old.pitch
                )


            new_obj.duration.quarterLength = use


            # remove musicxml leftovers
            new_obj.tie = None
            new_obj.beams = []


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



    # fill final measure

    if beat > 0:


        r = note.Rest()

        r.duration.quarterLength = round(
            4 - beat,
            2
        )

        m.append(r)

        part.append(m)



    result.append(part)


    return result





def check(score):

    print("V89 FINAL CHECK")


    for m in score.parts[0].getElementsByClass(
        "Measure"
    ):


        total = sum(
            n.duration.quarterLength
            for n in m.notesAndRests
        )


        print(
            "Measure",
            m.number,
            float(total)
        )


        if abs(total - 4.0) > 0.001:

            raise Exception(
                "BAD BAR " + str(m.number)
            )


    print("V89 SAFE")





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





if __name__ == "__main__":


    if len(sys.argv) < 3:

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        exit()


    clean(
        sys.argv[1],
        sys.argv[2]
    )