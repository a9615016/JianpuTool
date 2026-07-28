# clean_musicxml.py
# CLEAN MUSICXML V33
# STRICT 4/4 BAR NORMALIZER
# Jianpu compatible

import sys
from music21 import converter, stream, note, chord, meter


TARGET_BEATS = 4.0


def remove_problem_elements(score):

    print("remove voices")
    for p in score.parts:
        for el in list(p.recurse()):
            if hasattr(el, "voice"):
                try:
                    el.voice = None
                except:
                    pass

    print("remove chords")
    for p in score.parts:
        for c in list(p.recurse().getElementsByClass('Chord')):
            n = note.Note(c.pitches[0])
            n.duration = c.duration
            c.activeSite.replace(c, n)

    print("remove beams")
    for n in score.recurse().notes:
        try:
            n.beams = None
        except:
            pass

    print("remove ties")
    for n in score.recurse().notes:
        try:
            n.tie = None
        except:
            pass


def quantize_duration(score):

    print("duration quantize")

    allowed = [
        4.0,
        2.0,
        1.0,
        0.5,
        0.25,
        0.125
    ]

    for n in score.recurse().notesAndRests:

        q = min(
            allowed,
            key=lambda x: abs(x - n.duration.quarterLength)
        )

        n.duration.quarterLength = q



def rebuild_measures(score):

    print("rebuild measures")

    for p in score.parts:

        p.insert(0, meter.TimeSignature("4/4"))

        p.makeMeasures(inPlace=True)



def strict_fix_bars(score):

    print("STRICT BAR FIX")

    for p in score.parts:

        measures = list(p.getElementsByClass(
            "Measure"
        ))

        for m in measures:

            total = 0

            new_elements = []

            for el in m.notesAndRests:

                length = el.duration.quarterLength


                # 超過4拍直接停止
                if total + length > TARGET_BEATS:

                    remain = TARGET_BEATS - total

                    if remain > 0:

                        el.duration.quarterLength = remain
                        new_elements.append(el)

                    total = TARGET_BEATS
                    break


                new_elements.append(el)

                total += length



            # 不足補休止
            if total < TARGET_BEATS:

                r = note.Rest()
                r.duration.quarterLength = (
                    TARGET_BEATS - total
                )

                new_elements.append(r)


            m.clear()

            for el in new_elements:
                m.append(el)


def final_check(score):

    print("FINAL CHECK")

    ok = True

    for m in score.recurse().getElementsByClass(
        "Measure"
    ):

        length = sum(
            x.duration.quarterLength
            for x in m.notesAndRests
        )

        print(
            "Measure",
            m.number,
            length
        )


        if abs(length - 4.0) > 0.001:
            ok = False


    if ok:
        print("ALL MEASURES SAFE")

    else:
        print("WARNING measure mismatch")



def main():

    infile = sys.argv[1]

    outfile = (
        sys.argv[2]
        if len(sys.argv)>2
        else "clean.musicxml"
    )


    print("================")
    print(
        "CLEAN MUSICXML V33 "
        "STRICT 4/4"
    )
    print("================")


    print("read")

    score = converter.parse(infile)


    remove_problem_elements(score)

    quantize_duration(score)

    rebuild_measures(score)

    strict_fix_bars(score)

    rebuild_measures(score)

    final_check(score)


    print("FINAL WRITE")

    score.write(
        "musicxml",
        fp=outfile
    )


    print("DONE")
    print(outfile)



if __name__ == "__main__":
    main()