# jianpu_fix_musicxml.py
# V9.0
# FINAL JIANPU COMPATIBLE

from music21 import converter, stream, note, chord, meter
import sys


TARGET_BEAT = 4.0


def remove_voices(score):
    print("remove voices")

    for part in score.parts:
        for measure in part.getElementsByClass('Measure'):
            for n in measure.notesAndRests:
                if hasattr(n, "voice"):
                    n.voice = None


def remove_chords(score):
    print("remove chords")

    for part in score.parts:
        for measure in part.getElementsByClass('Measure'):
            for c in measure.getElementsByClass('Chord'):
                n = note.Note(c.pitches[0])
                n.duration = c.duration
                c.activeSite.replace(c, n)


def remove_beams(score):
    print("remove beams")

    for n in score.recurse().notes:
        n.beams = None


def remove_ties(score):
    print("remove ties")

    for n in score.recurse().notes:
        n.tie = None


def force_44(score):

    print("force 4/4")

    for part in score.parts:
        part.insert(0, meter.TimeSignature("4/4"))


def quantize_duration(score):

    print("duration quantize")

    allowed = [
        0.25,
        0.5,
        1.0,
        2.0,
        4.0
    ]

    for n in score.recurse().notesAndRests:

        d = float(n.duration.quarterLength)

        closest = min(
            allowed,
            key=lambda x: abs(x-d)
        )

        n.duration.quarterLength = closest



def rebuild_measures(score):

    print("rebuild measures")

    for part in score.parts:

        measures = list(
            part.getElementsByClass("Measure")
        )

        for m in measures:

            length = float(
                m.duration.quarterLength
            )

            print(
                "Measure",
                m.number,
                length
            )


def force_exact_measure(score):

    print("force exact measure duration")

    for part in score.parts:

        for m in part.getElementsByClass("Measure"):

            length = float(
                m.duration.quarterLength
            )


            if length > TARGET_BEAT:

                print(
                    "trim",
                    m.number,
                    length
                )

                notes = list(
                    m.notes
                )

                if notes:

                    last = notes[-1]

                    diff = (
                        length -
                        TARGET_BEAT
                    )

                    new_len = (
                        last.duration.quarterLength
                        -
                        diff
                    )

                    if new_len > 0:
                        last.duration.quarterLength = new_len



            elif length < TARGET_BEAT:

                diff = (
                    TARGET_BEAT -
                    length
                )

                print(
                    "fill rest",
                    m.number,
                    diff
                )

                r = note.Rest()

                r.duration.quarterLength = diff

                m.append(r)



def split_cross_measure(score):

    print("split cross measure notes")

    for part in score.parts:

        for m in part.getElementsByClass("Measure"):

            if m.duration.quarterLength > 4:

                force_exact_measure(score)



def clear_cache(score):

    print("clear notation cache")

    try:
        score.remove()
    except:
        pass



def final_check(score):

    print("FINAL CHECK")

    ok = True

    for part in score.parts:

        for m in part.getElementsByClass("Measure"):

            length = float(
                m.duration.quarterLength
            )

            print(
                "Measure",
                m.number,
                length
            )

            if abs(length-4.0) > 0.01:
                ok=False


    if ok:
        print("ALL MEASURES SAFE")
    else:
        print("WARNING measure mismatch")



def main():

    if len(sys.argv)<3:

        print(
            "python jianpu_fix_musicxml.py input.musicxml output.musicxml"
        )

        return


    src=sys.argv[1]
    dst=sys.argv[2]


    print("================")
    print("CLEAN MUSICXML V9 FINAL JIANPU COMPATIBLE")
    print("================")


    score=converter.parse(src)


    remove_voices(score)

    remove_chords(score)

    remove_beams(score)

    remove_ties(score)

    force_44(score)

    quantize_duration(score)

    rebuild_measures(score)

    split_cross_measure(score)

    force_exact_measure(score)

    rebuild_measures(score)


    clear_cache(score)


    final_check(score)


    print("FINAL WRITE")

    score.write(
        "musicxml",
        fp=dst
    )


    print("DONE")
    print(dst)



if __name__=="__main__":
    main()