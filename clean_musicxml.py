import sys
import music21
from music21 import note, chord, duration


print("================")
print("CLEAN MUSICXML V23.2 FINAL INDENT + DURATION SAFE")
print("================")


# =========================
# remove voices
# =========================

def remove_voices(score):

    print("remove voices")

    for part in score.parts:

        for n in part.recurse().notes:

            try:
                n.voice = None
            except:
                pass



# =========================
# remove chords
# =========================

def remove_chords(score):

    print("remove chords")

    for part in score.parts:

        for c in list(part.recurse().getElementsByClass("Chord")):

            try:

                n = note.Note(
                    c.root()
                )

                n.duration = c.duration

                c.activeSite.replace(
                    c,
                    n
                )

            except Exception as e:

                print(
                    "Chord skip:",
                    e
                )



# =========================
# beam safe reset
# =========================

def reset_beams(score):

    print("safe beam reset")

    for n in score.recurse().notes:

        try:
            n.beams = None

        except:
            pass



# =========================
# quantize duration
# =========================

def quantize(score):

    print("quantize")


    allowed = [
        4,
        2,
        1,
        0.5,
        0.25
    ]


    for n in score.recurse().notesAndRests:

        try:

            q = n.duration.quarterLength

            closest = min(
                allowed,
                key=lambda x:abs(x-q)
            )

            n.duration.quarterLength = closest


        except Exception as e:

            print(
                "quantize skip:",
                e
            )



# =========================
# FINAL REMOVE 128TH
# =========================

def remove_bad_duration(score):

    print("duration safe")


    for n in score.recurse().notesAndRests:


        try:

            q = n.duration.quarterLength


            # jianpu_ly 不支援 128th
            if q < 0.25:

                print(
                    "FIX SHORT:",
                    q
                )


                n.duration = duration.Duration(
                    0.25
                )


        except Exception as e:

            print(
                "duration skip:",
                e
            )



# =========================
# force 4/4
# =========================

def force_44(score):

    print("force 4/4")


    for part in score.parts:

        part.insert(
            0,
            music21.meter.TimeSignature("4/4")
        )



# =========================
# rebuild measures
# =========================

def rebuild(score):

    print("rebuild measures")

    score.makeMeasures(
        inPlace=True
    )



# =========================
# check
# =========================

def check(score):

    print("check measures")


    for i,m in enumerate(
        score.recurse()
        .getElementsByClass("Measure")
    ):

        try:

            print(
                "Measure",
                i+1,
                m.barDuration.quarterLength
            )

        except:

            pass



# =========================
# main clean
# =========================

def clean_musicxml(
        inp,
        out
):

    print("read")


    score = music21.converter.parse(
        inp
    )


    remove_voices(score)


    remove_chords(score)


    reset_beams(score)


    quantize(score)


    print("FINAL NOTE SPLIT")


    # V23 保留


    remove_bad_duration(score)


    force_44(score)


    rebuild(score)


    reset_beams(score)


    check(score)


    print("write")


    score.write(
        "musicxml",
        fp=out
    )


    print()

    print(
        "DONE",
        out
    )



# =========================
# run
# =========================

if __name__ == "__main__":


    if len(sys.argv) < 3:

        print(
            "usage: python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit(1)


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )