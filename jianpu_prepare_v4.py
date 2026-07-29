# jianpu_prepare_v4.py
# JianpuTool V4
# Fix jianpu_ly barcheck fail

import sys
from music21 import converter, stream, note, chord, meter


ALLOW = [
    0.25,
    0.5,
    0.75,
    1.0,
    1.5,
    2.0,
    3.0,
    4.0
]


def quantize_duration(value):

    return min(
        ALLOW,
        key=lambda x: abs(x-value)
    )


def remove_bad_elements(score):

    for p in score.parts:

        for n in list(p.recurse()):

            # remove chord
            if isinstance(n, chord.Chord):

                new_note = note.Note(
                    n.pitches[0]
                )

                new_note.duration = n.duration

                n.activeSite.replace(
                    n,
                    new_note
                )


            # remove tie
            if hasattr(n, "tie"):
                n.tie = None



def fix_measure(m):

    target = 4.0


    current = sum(
        n.duration.quarterLength
        for n in m.notesAndRests
    )


    # duration quantize
    for n in m.notesAndRests:

        q = quantize_duration(
            n.duration.quarterLength
        )

        n.duration.quarterLength = q



    current = sum(
        n.duration.quarterLength
        for n in m.notesAndRests
    )


    # too long -> trim
    if current > target:

        overflow = current-target


        for n in reversed(
            list(m.notesAndRests)
        ):

            if overflow <= 0:
                break


            d=n.duration.quarterLength


            if d > overflow:

                n.duration.quarterLength = d-overflow
                overflow=0

            else:

                m.remove(n)
                overflow-=d



    # too short fill rest
    current = sum(
        n.duration.quarterLength
        for n in m.notesAndRests
    )


    if current < target:

        r = note.Rest()

        r.duration.quarterLength = (
            target-current
        )

        m.append(r)



def prepare(src,dst):

    print(
        "######## JIANPU PREPARE V4 ########"
    )


    score = converter.parse(src)


    score.insert(
        0,
        meter.TimeSignature("4/4")
    )


    remove_bad_elements(score)



    for p in score.parts:


        measures = p.makeMeasures()


        print(
            "TOTAL MEASURES:",
            len(measures)
        )


        for i,m in enumerate(measures):


            fix_measure(m)


            length=sum(
                n.duration.quarterLength
                for n in m.notesAndRests
            )


            print(
                "Measure",
                i+1,
                length
            )



    score.write(
        "musicxml",
        fp=dst
    )


    print(
        "######## V4 DONE ########"
    )

    print(dst)



if __name__=="__main__":


    if len(sys.argv)<3:

        print(
            "python jianpu_prepare_v4.py input.xml output.xml"
        )

        exit()


    prepare(
        sys.argv[1],
        sys.argv[2]
    )