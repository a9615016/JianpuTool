from music21 import converter, note, chord, meter, stream, duration
import sys


print("==============================")
print("JIANPU PREPARE V3")
print("==============================")


VALID_DURATIONS = [
    0.25,
    0.5,
    0.75,
    1,
    1.5,
    2,
    3,
    4
]


def quantize_duration(x):

    return min(
        VALID_DURATIONS,
        key=lambda d: abs(d-x)
    )


def remove_chords(score):

    print("remove chords")

    for c in list(
        score.recurse()
        .getElementsByClass(chord.Chord)
    ):

        n = note.Note(
            c.root()
        )

        n.duration = c.duration

        c.activeSite.replace(
            c,
            n
        )


def clean_notes(score):

    print("duration quantize")

    for n in score.recurse().notes:

        old = n.duration.quarterLength

        new = quantize_duration(old)

        if old != new:
            print(
                "duration",
                old,
                "=>",
                new
            )

        n.duration.quarterLength = new


def remove_articulation(score):

    print("remove notation")

    for n in score.recurse().notes:

        n.tie = None

        try:
            n.beams = []
        except:
            pass


def force_time(score):

    print("force 4/4")

    for p in score.parts:

        p.insert(
            0,
            meter.TimeSignature("4/4")
        )


def rebuild_measure(score):

    print("rebuild measures")

    for p in score.parts:

        p.makeMeasures(
            inPlace=True
        )


def fix_measure(score):

    print("================")
    print("FIX MEASURE")
    print("================")

    for p in score.parts:

        measures = list(
            p.getElementsByClass("Measure")
        )

        for m in measures:

            total = sum(
                n.duration.quarterLength
                for n in m.notesAndRests
            )


            if total > 4:

                print(
                    "OVER",
                    m.number,
                    total
                )


                while total > 4:

                    m.splitAtDurations()


            elif total < 4:

                rest = note.Rest()

                rest.duration.quarterLength = (
                    4-total
                )

                m.append(rest)



def final_check(score):

    print("================")
    print("FINAL CHECK")
    print("================")

    for i,m in enumerate(
        score.parts[0]
        .getElementsByClass("Measure"),
        1
    ):

        total=sum(
            n.duration.quarterLength
            for n in m.notesAndRests
        )

        print(
            "Measure",
            i,
            total
        )


        if abs(total-4)>0.01:

            print(
                "WARNING",
                i,
                total
            )



def main():

    if len(sys.argv)<3:

        print(
            "python jianpu_prepare_v3.py input.musicxml output.musicxml"
        )

        return


    infile=sys.argv[1]
    outfile=sys.argv[2]


    print("READ")

    score=converter.parse(
        infile
    )


    remove_chords(score)

    clean_notes(score)

    remove_articulation(score)

    force_time(score)

    rebuild_measure(score)

    fix_measure(score)

    rebuild_measure(score)

    final_check(score)


    print("WRITE")

    score.write(
        "musicxml",
        fp=outfile
    )


    print("DONE")
    print(outfile)



if __name__=="__main__":
    main()