# CLEAN MUSICXML V40
# JIANPU COMPATIBLE
# 2026-07-28

import sys
from music21 import converter, stream, meter, note, chord, tie


def clean_musicxml(input_file, output_file):

    print("================")
    print("CLEAN MUSICXML V40 FINAL JIANPU")
    print("================")


    print("read")

    score = converter.parse(input_file)


    # -----------------------
    # remove voices
    # -----------------------
    print("remove voices")

    for part in score.parts:
        for n in part.recurse():
            if hasattr(n, "voice"):
                n.voice = None


    # -----------------------
    # remove chords
    # -----------------------
    print("remove chords")

    for c in score.recurse().getElementsByClass(chord.Chord):

        if len(c.pitches):

            n = note.Note(c.pitches[0])
            n.duration = c.duration

            c.activeSite.replace(c, n)



    # -----------------------
    # remove beams
    # -----------------------
    print("remove beams")

    for n in score.recurse().notes:

        try:
            n.beams = []
        except:
            pass



    # -----------------------
    # remove ties
    # -----------------------
    print("remove ties")

    for n in score.recurse().notes:

        try:
            n.tie = None
        except:
            pass



    # -----------------------
    # force 4/4
    # -----------------------
    print("force 4/4")

    for part in score.parts:

        part.insert(
            0,
            meter.TimeSignature("4/4")
        )



    # -----------------------
    # duration quantize
    # -----------------------
    print("duration quantize")

    for n in score.recurse().notesAndRests:

        q = float(n.duration.quarterLength)

        allowed = [
            0.25,
            0.5,
            0.75,
            1,
            1.5,
            2,
            3,
            4
        ]

        closest = min(
            allowed,
            key=lambda x:abs(x-q)
        )

        n.duration.quarterLength = closest



    # -----------------------
    # rebuild measures
    # -----------------------
    print("rebuild measures")

    score = score.makeMeasures(
        inPlace=False
    )



    # -----------------------
    # split cross measure notes
    # -----------------------
    print("split cross measure notes")

    for part in score.parts:

        try:
            part.makeMeasures(
                inPlace=True
            )
        except:
            pass



    # -----------------------
    # force truncate overflow
    # -----------------------
    print("FORCE TRUNCATE OVERFLOW NOTES")


    for part in score.parts:

        measures = (
            part
            .getElementsByClass(stream.Measure)
        )


        for m in measures:

            total = 0

            keep=[]


            for e in m.notesAndRests:

                dur=float(
                    e.duration.quarterLength
                )


                if total + dur > 4:

                    remain = 4-total


                    if remain > 0:

                        e.duration.quarterLength = remain
                        keep.append(e)


                        print(
                            "TRUNCATE",
                            "Measure",
                            m.number,
                            remain
                        )


                    break


                else:

                    keep.append(e)

                    total += dur



            # clear old
            for e in list(
                m.notesAndRests
            ):
                m.remove(e)


            # insert new

            offset=0

            for e in keep:

                m.insert(
                    offset,
                    e
                )

                offset += e.duration.quarterLength



    # -----------------------
    # final check
    # -----------------------
    print("clear notation cache")


    print("FINAL HARD CHECK")


    for m in score.parts[0].getElementsByClass(stream.Measure):

        length=float(
            m.duration.quarterLength
        )

        print(
            "Measure",
            m.number,
            length
        )


        if length > 4.001:

            print(
                "WARNING measure mismatch"
            )



    print("FINAL WRITE")


    score.write(
        "musicxml",
        fp=output_file
    )


    print("DONE")
    print(output_file)



if __name__ == "__main__":


    if len(sys.argv)<3:

        print(
            "usage:"
            " python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit()


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )