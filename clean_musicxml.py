# clean_musicxml.py
# CLEAN MUSICXML V27 FINAL REBUILD
# Jianpu_ly compatible

import sys
from music21 import converter, stream, note, meter


GRID = 0.25


def quantize(x):
    return round(x / GRID) * GRID


def clean_musicxml(src, dst):

    print("================")
    print("CLEAN MUSICXML V27 FINAL REBUILD")
    print("================")

    print("read")

    old_score = converter.parse(src)


    print("create new score")

    new_score = stream.Score()


    for old_part in old_score.parts:

        print("rebuild part")

        new_part = stream.Part()

        new_part.insert(
            0,
            meter.TimeSignature("4/4")
        )


        notes = []


        for n in old_part.recurse().notesAndRests:

            if isinstance(n, note.Note):

                nn = note.Note(
                    n.pitch
                )

                nn.duration.quarterLength = quantize(
                    n.duration.quarterLength
                )

                notes.append(nn)


            elif isinstance(n, note.Rest):

                rr = note.Rest()

                rr.duration.quarterLength = quantize(
                    n.duration.quarterLength
                )

                notes.append(rr)



        print(
            "notes:",
            len(notes)
        )


        # 防止過短音符
        for n in notes:

            if n.duration.quarterLength < 0.25:

                n.duration.quarterLength = 0.25



        # 重新建立 measures

        m = stream.Measure(
            number=1
        )

        total = 0
        measure_no = 1


        for n in notes:

            length = n.duration.quarterLength


            if total + length > 4:

                remain = 4 - total

                if remain > 0:

                    r = note.Rest()
                    r.duration.quarterLength = remain
                    m.append(r)


                new_part.append(m)

                measure_no += 1

                m = stream.Measure(
                    number=measure_no
                )

                total = 0



            m.append(n)

            total += length



        if total < 4:

            r = note.Rest()
            r.duration.quarterLength = 4-total
            m.append(r)


        new_part.append(m)


        new_score.append(
            new_part
        )


    print("FINAL CHECK")


    for part in new_score.parts:

        for m in part.getElementsByClass("Measure"):

            length = m.duration.quarterLength

            print(
                "Measure",
                m.number,
                length
            )


    print("WRITE")

    new_score.write(
        "musicxml",
        fp=dst
    )


    print("DONE")
    print(dst)



if __name__ == "__main__":

    if len(sys.argv) < 3:

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit(1)


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )