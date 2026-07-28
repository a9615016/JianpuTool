# clean_musicxml.py
# CLEAN MUSICXML V26 OFFSET QUANTIZE
# Jianpu_ly compatible

import sys
from music21 import converter, stream, meter, note, chord, duration


def quantize_value(x, grid=0.25):
    return round(x / grid) * grid


def clean_score(src, dst):

    print("================")
    print("CLEAN MUSICXML V26 OFFSET QUANTIZE")
    print("================")

    print("read")
    score = converter.parse(src)


    print("remove voices")
    for part in score.parts:
        for m in part.getElementsByClass('Measure'):
            for n in list(m.notesAndRests):
                if n.hasStyleInformation:
                    pass


    print("remove chords")
    for part in score.parts:
        for c in list(part.recurse().getElementsByClass('Chord')):
            pitches = c.pitches
            if pitches:
                n = note.Note(pitches[0])
                n.duration = c.duration
                c.activeSite.replace(c, n)


    print("remove beams")
    for n in score.recurse().notes:
        try:
            n.beams = []
        except:
            pass


    print("remove ties")
    for n in score.recurse().notes:
        try:
            n.tie = None
        except:
            pass


    print("force 4/4")
    for part in score.parts:
        part.insert(0, meter.TimeSignature("4/4"))


    print("duration quantize")

    for part in score.parts:

        for n in part.recurse().notesAndRests:

            q = n.duration.quarterLength

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
                key=lambda x: abs(x-q)
            )

            n.duration.quarterLength = closest



    print("OFFSET QUANTIZE")

    for part in score.parts:

        for n in part.recurse().notesAndRests:

            try:
                new_offset = quantize_value(
                    n.offset,
                    0.25
                )

                n.offset = new_offset

            except:
                pass



    print("rebuild measures")

    for part in score.parts:

        part.makeMeasures(
            inPlace=True
        )


    print("split cross measure notes")

    for part in score.parts:

        for m in part.getElementsByClass("Measure"):

            for n in list(m.notesAndRests):

                try:

                    end = n.offset + n.duration.quarterLength

                    if end > 4:

                        remain = 4 - n.offset

                        if remain > 0:
                            n.duration.quarterLength = remain

                except:
                    pass



    print("rebuild measures")

    for part in score.parts:
        part.makeMeasures(
            inPlace=True
        )


    print("fill measure rest")

    for part in score.parts:

        for m in part.getElementsByClass("Measure"):

            total = 0

            for n in m.notesAndRests:
                total += n.duration.quarterLength


            if total < 4:

                r = note.Rest()
                r.duration.quarterLength = 4-total
                m.append(r)



    print("rebuild measures")

    for part in score.parts:
        part.makeMeasures(
            inPlace=True
        )


    print("clear notation cache")

    try:
        score.coreElementsChanged()
    except:
        pass



    print("FINAL CHECK")

    for part in score.parts:

        for m in part.getElementsByClass("Measure"):

            length = m.barDuration.quarterLength

            print(
                "Measure",
                m.number,
                length
            )

            if abs(length-4) > 0.01:
                print(
                    "WARNING",
                    m.number
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


    clean_score(
        sys.argv[1],
        sys.argv[2]
    )