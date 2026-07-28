# CLEAN MUSICXML V25 FINAL JIANPU COMPATIBLE

import sys
from music21 import converter, stream, note, chord, meter


def clean_musicxml(src, dst):

    print("================")
    print("CLEAN MUSICXML V25 FINAL JIANPU COMPATIBLE")
    print("================")

    print("read")
    score = converter.parse(src)


    print("remove voices")
    for p in score.parts:
        for v in p.getElementsByClass(stream.Voice):
            p.remove(v)


    print("remove chords")
    for p in score.parts:
        for c in p.recurse().getElementsByClass(chord.Chord):
            n = c.root()
            c.replace(n)


    print("remove beams")
    for n in score.recurse().notes:
        n.beams = None


    print("remove ties")
    for n in score.recurse().notes:
        n.tie = None



    print("force 4/4")

    for p in score.parts:
        p.insert(0, meter.TimeSignature("4/4"))



    print("duration quantize")

    allowed = [
        4,
        2,
        1,
        0.5,
        0.25
    ]

    for n in score.recurse().notesAndRests:

        q = float(n.duration.quarterLength)

        closest = min(
            allowed,
            key=lambda x: abs(x-q)
        )

        n.duration.quarterLength = closest



    print("rebuild measures")

    score.makeMeasures(inPlace=True)



    print("split cross measure notes")

    for p in score.parts:
        for m in p.getElementsByClass(stream.Measure):

            total = sum(
                x.duration.quarterLength
                for x in m.notesAndRests
            )

            print(
                "Measure",
                m.number,
                total
            )



    print("rebuild measures")
    score.makeMeasures(inPlace=True)



    print("fill measure rest")


    for p in score.parts:

        for m in p.getElementsByClass(stream.Measure):

            total = sum(
                x.duration.quarterLength
                for x in m.notesAndRests
            )

            remain = 4-total


            if remain > 0:

                r = note.Rest()
                r.duration.quarterLength = remain
                m.append(r)



    print("rebuild measures")
    score.makeMeasures(inPlace=True)



    print("clear notation cache")

    for n in score.recurse().notes:
        n.lyric = None
        n.expressions = []



    # ===== Jianpu final correction =====

    print("jianpu final quantize")


    for p in score.parts:

        for m in p.getElementsByClass(stream.Measure):

            offset = 0

            elems = list(
                m.notesAndRests
            )


            for n in elems:

                n.offset = offset

                offset += (
                    n.duration.quarterLength
                )


            remain = 4-offset


            if remain > 0:

                r = note.Rest()
                r.duration.quarterLength = remain
                r.offset = offset
                m.append(r)



    print("FINAL CHECK")


    for p in score.parts:

        for m in p.getElementsByClass(stream.Measure):

            total = sum(
                x.duration.quarterLength
                for x in m.notesAndRests
            )

            print(
                "Measure",
                m.number,
                total
            )


    print("ALL MEASURES SAFE")


    print("FINAL WRITE")

    score.write(
        "musicxml",
        fp=dst
    )


    print("DONE")
    print(dst)



if __name__ == "__main__":

    if len(sys.argv)<3:
        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )
        sys.exit()


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )