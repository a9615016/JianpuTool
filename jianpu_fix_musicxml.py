# jianpu_fix_musicxml.py
# V10.0 FINAL JIANPU COMPATIBLE
# MIDI/BasicPitch MusicXML 修復版

import sys
from music21 import converter, stream, note, chord, meter, duration


def quantize_duration(n):
    """
    強制節奏量化
    """
    q = n.quarterLength

    values = [
        0.25,
        0.5,
        1.0,
        2.0,
        4.0
    ]

    best = min(values, key=lambda x: abs(x-q))

    n.duration = duration.Duration(best)

    return n


def clean_notes(score):

    print("remove voices")

    for part in score.parts:

        # remove voices
        for v in list(part.recurse().getElementsByClass('Voice')):
            v.activeSite.remove(v)


        print("remove chords")

        for c in list(part.recurse().getElementsByClass('Chord')):
            new_notes = []
            for p in c.pitches:
                n = note.Note(p)
                n.duration = c.duration
                new_notes.append(n)

            if c.activeSite:
                idx = c.activeSite.index(c)
                c.activeSite.pop(idx)
                for n in reversed(new_notes):
                    c.activeSite.insert(idx,n)



        print("remove beams")
        print("remove ties")


        for n in part.recurse().notes:

            if isinstance(n, note.Note):

                # remove ties
                n.tie = None

                # quantize
                quantize_duration(n)


            elif isinstance(n, chord.Chord):

                quantize_duration(n)


    return score



def rebuild_measure(score):

    print("force 4/4")

    for part in score.parts:

        part.insert(
            0,
            meter.TimeSignature("4/4")
        )


    print("rebuild measures")

    score.makeMeasures(
        inPlace=True
    )


def split_overflow(score):

    print("split cross measure notes")

    for part in score.parts:

        measures = part.getElementsByClass(
            stream.Measure
        )

        for m in measures:

            total = 0

            for n in m.notesAndRests:

                total += n.quarterLength


            if total > 4:

                print(
                    "overflow fix:",
                    m.number,
                    total
                )


                diff = total - 4

                for n in reversed(m.notes):

                    if diff <= 0:
                        break

                    if n.quarterLength > diff:

                        n.duration = duration.Duration(
                            n.quarterLength - diff
                        )

                        diff = 0

                    else:

                        diff -= n.quarterLength
                        n.duration = duration.Duration(0)


def fill_rest(score):

    print("fill measure rest")

    for part in score.parts:

        for m in part.getElementsByClass(stream.Measure):

            total = sum(
                x.quarterLength
                for x in m.notesAndRests
            )

            if total < 4:

                r = note.Rest()
                r.duration = duration.Duration(
                    4-total
                )

                m.append(r)



def final_check(score):

    print("FINAL CHECK")

    ok = True

    for part in score.parts:

        for m in part.getElementsByClass(stream.Measure):

            length = sum(
                x.quarterLength
                for x in m.notesAndRests
            )

            print(
                "Measure",
                m.number,
                length
            )

            if abs(length-4)>0.001:
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

    if len(sys.argv)<3:
        print(
            "python jianpu_fix_musicxml.py input.musicxml output.musicxml"
        )
        return


    inp=sys.argv[1]
    out=sys.argv[2]


    print("================")
    print(
        "CLEAN MUSICXML V10 FINAL JIANPU"
    )
    print("================")


    print("read")

    score = converter.parse(inp)


    score = clean_notes(score)

    rebuild_measure(score)

    split_overflow(score)

    rebuild_measure(score)

    fill_rest(score)

    rebuild_measure(score)


    print("clear notation cache")


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