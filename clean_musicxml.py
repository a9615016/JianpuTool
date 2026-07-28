# clean_musicxml.py
# CLEAN MUSICXML V34
# STRICT 4/4 + SPLIT CROSS BAR NOTES
# Jianpu compatible

import sys
from music21 import converter, note, chord, meter


BAR_LENGTH = 4.0


def remove_problem(score):

    print("remove voices")

    for n in score.recurse().notes:

        try:
            n.tie = None
        except:
            pass


    print("remove chords")

    for c in list(score.recurse().getElementsByClass("Chord")):

        n = note.Note(c.pitches[0])

        n.duration = c.duration

        c.activeSite.replace(c, n)



    print("remove beams")

    for n in score.recurse().notes:

        try:
            n.beams = None
        except:
            pass



def quantize(score):

    print("duration quantize")

    values = [
        4,
        2,
        1,
        0.5,
        0.25,
        0.125
    ]

    for n in score.recurse().notesAndRests:

        q = min(
            values,
            key=lambda x:
            abs(x-n.duration.quarterLength)
        )

        n.duration.quarterLength = q



def split_measure_notes(score):

    print("SPLIT LONG NOTES")

    for part in score.parts:

        measures = list(
            part.getElementsByClass("Measure")
        )

        for m in measures:

            new_elements = []

            used = 0


            for el in list(m.notesAndRests):

                dur = el.duration.quarterLength


                while dur > 0:


                    remain = BAR_LENGTH - used


                    take = min(
                        dur,
                        remain
                    )


                    new_el = el.__class__(
                        el.pitch
                        if hasattr(el, "pitch")
                        else None
                    )


                    if isinstance(el, note.Rest):

                        new_el = note.Rest()



                    elif isinstance(el, note.Note):

                        new_el = note.Note(
                            el.pitch
                        )


                    new_el.duration.quarterLength = take


                    new_elements.append(new_el)


                    dur -= take

                    used += take



                    if used >= BAR_LENGTH:

                        used = 0



            if used < BAR_LENGTH:

                r = note.Rest()

                r.duration.quarterLength = (
                    BAR_LENGTH-used
                )

                new_elements.append(r)



            m.clear()

            for e in new_elements:

                m.append(e)



def check(score):

    print("FINAL CHECK")


    ok=True


    for m in score.recurse().getElementsByClass(
        "Measure"
    ):

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

        print(
            "ALL MEASURES SAFE"
        )

    else:

        print(
            "WARNING measure mismatch"
        )



def main():

    infile=sys.argv[1]

    outfile=(
        sys.argv[2]
        if len(sys.argv)>2
        else "clean.musicxml"
    )


    print("================")
    print(
        "CLEAN MUSICXML V34"
    )
    print(
        "STRICT 4/4 + SPLIT"
    )
    print("================")


    print("read")


    score=converter.parse(infile)


    remove_problem(score)


    quantize(score)


    print("force 4/4")

    for p in score.parts:

        p.insert(
            0,
            meter.TimeSignature("4/4")
        )


    print("rebuild measures")

    score.makeMeasures(
        inPlace=True
    )


    split_measure_notes(score)


    check(score)


    print("FINAL WRITE")


    score.write(
        "musicxml",
        fp=outfile
    )


    print("DONE")

    print(outfile)



if __name__=="__main__":

    main()