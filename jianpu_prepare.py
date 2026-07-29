from music21 import converter, stream, note, chord, meter
import sys
import os


print("==============================")
print("JIANPU PREPARE V2")
print("==============================")


VALID_DURATIONS = [
    0.5,    # 16分
    0.75,
    1,      # 8分
    1.5,
    2,      # 4分
    3,
    4,      # 2分
    6,
    8,      # 全音符
    12
]


def quantize_duration(value):

    return min(
        VALID_DURATIONS,
        key=lambda x: abs(x - value)
    )


def remove_chords(score):

    print("remove chords")

    for c in score.recurse().getElementsByClass(chord.Chord):

        n = note.Note(
            c.root().pitch
        )

        n.duration = c.duration

        c.activeSite.replace(
            c,
            n
        )


def clean_notes(score):

    print("quantize duration")

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



def remove_notation(score):

    print("remove notation")

    for n in score.recurse().notes:

        n.tie = None

        try:
            n.beams = []
        except:
            pass



def force_44(score):

    print("force 4/4")

    for p in score.parts:

        p.insert(
            0,
            meter.TimeSignature("4/4")
        )



def rebuild(score):

    print("rebuild measures")

    for p in score.parts:

        p.makeMeasures(
            inPlace=True
        )


def check(score):

    print("================")
    print("FINAL CHECK")
    print("================")

    for i,m in enumerate(
        score.parts[0].getElementsByClass("Measure"),
        1
    ):

        total = 0

        for n in m.notesAndRests:

            total += n.duration.quarterLength


        print(
            "Measure",
            i,
            total
        )


        if total > 4.01:

            print(
                "WARNING",
                i,
                total
            )



def main():

    if len(sys.argv)<3:

        print(
            "python jianpu_prepare_v2.py input.musicxml output.musicxml"
        )

        return


    infile=sys.argv[1]

    outfile=sys.argv[2]


    print("READ")

    score = converter.parse(
        infile
    )


    remove_chords(score)

    clean_notes(score)

    remove_notation(score)

    force_44(score)

    rebuild(score)


    check(score)


    print("WRITE")

    score.write(
        "musicxml",
        fp=outfile
    )


    print("DONE")

    print(outfile)



if __name__=="__main__":

    main()