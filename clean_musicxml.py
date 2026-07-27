import sys
from music21 import converter
from music21 import stream
from music21 import note
from music21 import chord
from music21 import meter
from music21 import duration


VERSION = "CLEAN MUSICXML V23.3.1 FINAL JIANPU SAFE"


def remove_bad(score):

    print("remove voices")
    print("remove chords")

    for part in score.parts:

        for el in list(part.recurse()):

            if isinstance(el, chord.Chord):
                try:
                    el.activeSite.remove(el)
                except:
                    pass


def remove_beam_tie(score):

    print("remove beams")
    print("remove ties")

    for n in score.recurse().notes:

        try:
            n.beams = []
        except:
            pass

        try:
            n.tie = None
        except:
            pass


def remove_dots(score):

    print("remove dots")

    for n in score.recurse().notes:

        try:
            n.duration.dots = 0
        except:
            pass



def duration_safe(score):

    print("duration safe")

    allowed = [
        0.25,
        0.5,
        1,
        2,
        4
    ]

    for n in score.recurse().notes:

        q = float(n.duration.quarterLength)

        best = min(
            allowed,
            key=lambda x: abs(x-q)
        )

        n.duration = duration.Duration(best)



def force_meter(score):

    print("force 4/4")

    for part in score.parts:

        ts = part.recurse().getElementsByClass(
            meter.TimeSignature
        )

        if len(ts)==0:
            part.insert(
                0,
                meter.TimeSignature("4/4")
            )



def rebuild(score):

    print("make notation")

    try:
        score.makeNotation(
            inPlace=True
        )
    except Exception as e:
        print(e)



def clean_musicxml(input_file, output_file):

    print("================")
    print(VERSION)
    print("================")

    print("read")

    score = converter.parse(
        input_file
    )


    remove_bad(score)

    remove_beam_tie(score)

    remove_dots(score)

    duration_safe(score)

    force_meter(score)

    rebuild(score)

    remove_beam_tie(score)

    duration_safe(score)


    print("check measures")

    for part in score.parts:

        for m in part.getElementsByClass(
            stream.Measure
        ):
            print(
                "Measure",
                m.number,
                float(m.duration.quarterLength)
            )


    print("write")

    score.write(
        "musicxml",
        fp=output_file
    )


    print()
    print(
        "DONE",
        output_file
    )



if __name__=="__main__":

    if len(sys.argv)<3:

        print(
            "usage: python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit(1)


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )