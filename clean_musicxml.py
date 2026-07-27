from music21 import converter, stream, note, chord, beam
import sys
import os


VERSION = "CLEAN MUSICXML V23.3.2 FINAL BEAM OBJECT SAFE"


def safe_remove_beams(score):

    print("remove beams")

    for n in score.recurse().notes:

        try:
            # 正確清除 beams
            n.beams = None

        except Exception:
            pass



def safe_remove_ties(score):

    print("remove ties")

    for n in score.recurse().notes:

        try:
            n.tie = None
        except:
            pass



def remove_chords(score):

    print("remove chords")

    for c in list(score.recurse().getElementsByClass(chord.Chord)):

        try:
            highest = c.closedPosition()

            if highest:
                n = note.Note(
                    highest[0].pitch
                )
                n.duration = c.duration

                c.activeSite.replace(c, n)

        except:
            pass



def remove_voices(score):

    print("remove voices")

    for v in score.recurse().getElementsByClass("Voice"):

        try:
            v.activeSite.remove(v)

        except:
            pass



def duration_safe(score):

    print("duration safe")

    for n in score.recurse().notes:

        try:

            if n.duration.quarterLength <= 0:
                n.duration.quarterLength = 1

            # 避免 128th
            if n.duration.type == "128th":
                n.duration.quarterLength = 0.125

        except:
            pass



def force_measure(score):

    print("force 4/4")

    for p in score.parts:

        try:
            p.insert(
                0,
                __import__(
                    "music21"
                ).meter.TimeSignature("4/4")
            )

        except:
            pass



def check_measure(score):

    print("check measures")

    for i,m in enumerate(
        score.recurse().getElementsByClass("Measure"),
        1
    ):

        try:
            print(
                "Measure",
                i,
                m.duration.quarterLength
            )

        except:
            pass



def clean_musicxml(input_file, output_file):

    print("================")
    print(VERSION)
    print("================")

    print("read")

    score = converter.parse(input_file)


    remove_voices(score)

    remove_chords(score)

    safe_remove_beams(score)

    safe_remove_ties(score)

    duration_safe(score)

    force_measure(score)


    print("rebuild measures")


    # 不呼叫 makeNotation
    # 避免 music21 重新產生 beams


    safe_remove_beams(score)

    safe_remove_ties(score)


    check_measure(score)


    print("write")


    score.write(
        "musicxml",
        fp=output_file
    )


    print()
    print("DONE", output_file)



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