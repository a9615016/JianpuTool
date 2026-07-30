VERSION = "V31"

print("CLEAN MUSICXML", VERSION)

from music21 import converter, stream, note, chord, meter
import sys


def remove_chords(part):
    for el in list(part.recurse()):
        if isinstance(el, chord.Chord):
            n = note.Note(el.pitch)
            n.duration = el.duration
            el.activeSite.replace(el, n)


def remove_ties(part):
    for n in part.recurse().notes:
        if n.tie:
            n.tie = None


def remove_beams(part):
    for n in part.recurse().notes:
        n.beams = None


def force_44(score):
    for p in score.parts:
        p.insert(0, meter.TimeSignature("4/4"))


def quantize_duration(part):
    allowed = [
        4, 3, 2, 1,
        0.5, 0.25,
        1.5, 0.75
    ]

    for n in part.recurse().notes:
        q = float(n.duration.quarterLength)

        best = min(
            allowed,
            key=lambda x: abs(x-q)
        )

        n.duration.quarterLength = best


def split_cross_measure(part):

    print("split cross measure notes")

    measures = list(part.getElementsByClass("Measure"))

    for m in measures:
        total = m.duration.quarterLength

        if total > 4:

            print(
                "overflow measure",
                m.number,
                total
            )

            excess = total - 4

            notes = list(
                m.notes
            )

            for n in reversed(notes):

                if excess <= 0:
                    break

                length = n.duration.quarterLength

                if length > excess:
                    n.duration.quarterLength = length - excess
                    excess = 0

                else:
                    m.remove(n)
                    excess -= length



def rebuild_measures(score):

    print("rebuild measures")

    for p in score.parts:

        measures = p.makeMeasures()

        p.remove(
            p.getElementsByClass("Measure")
        )

        for m in measures:
            p.append(m)



def final_check(score):

    print("================")
    print("FINAL CHECK V31")
    print("================")

    for p in score.parts:

        for m in p.getElementsByClass("Measure"):

            q = float(
                m.duration.quarterLength
            )

            print(
                "Measure",
                m.number,
                q
            )

            if q > 4.01:
                print(
                    "WARNING overflow",
                    m.number,
                    q
                )



def main():

    if len(sys.argv) < 2:
        print(
            "usage: python clean_musicxml.py input.musicxml output.musicxml"
        )
        return


    infile = sys.argv[1]
    outfile = sys.argv[2]


    print("INPUT", infile)


    score = converter.parse(infile)


    print("remove chords")

    for p in score.parts:
        remove_chords(p)


    print("remove ties")

    for p in score.parts:
        remove_ties(p)


    print("remove beams")

    for p in score.parts:
        remove_beams(p)


    print("force 4/4")

    force_44(score)


    print("duration quantize")

    for p in score.parts:
        quantize_duration(p)


    split_cross_measure(score.parts[0])


    rebuild_measures(score)


    final_check(score)


    score.write(
        "musicxml",
        fp=outfile
    )


    print(
        "DONE",
        outfile
    )


if __name__ == "__main__":
    main()