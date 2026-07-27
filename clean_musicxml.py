import sys
import music21
from music21 import stream, note, chord, meter


VALID_DURATIONS = [
    0.25,
    0.5,
    0.75,
    1,
    1.5,
    2,
    3,
    4,
    6,
    8,
    12
]


def nearest_duration(value):
    return min(
        VALID_DURATIONS,
        key=lambda x: abs(x - value)
    )


def clean(input_file, output_file):

    print("================")
    print("CLEAN MUSICXML")
    print("================")

    print("input:", input_file)

    score = music21.converter.parse(input_file)


    # ----------------------
    # remove voices
    # ----------------------
    print("remove voices")

    for part in score.parts:
        for v in list(part.recurse().getElementsByClass('Voice')):
            v.activeSite.remove(v)


    # ----------------------
    # remove chords
    # ----------------------
    print("remove chords")

    for c in list(score.recurse().getElementsByClass('Chord')):

        pitches = c.pitches

        if len(pitches) > 0:

            n = note.Note(
                pitches[0]
            )

            n.duration = c.duration

            c.activeSite.replace(
                c,
                n
            )


    # ----------------------
    # quantize
    # ----------------------
    print("quantize")

    try:
        score.quantize(
            quarterLengthDivisors=[
                4,
                2,
                1
            ]
        )
    except:
        pass


    # ----------------------
    # force 4/4
    # ----------------------
    print("force 4/4")

    for part in score.parts:

        part.insert(
            0,
            meter.TimeSignature("4/4")
        )


    # ----------------------
    # fix duration
    # ----------------------
    print("fix duration")


    for n in score.recurse().notes:

        q = float(
            n.duration.quarterLength
        )


        # 非法 duration
        if q not in VALID_DURATIONS:

            new_q = nearest_duration(q)

            print(
                "fix duration:",
                q,
                "->",
                new_q
            )

            n.duration.quarterLength = new_q



    # ----------------------
    # remove empty measures
    # ----------------------
    print("remove empty measures")

    for m in list(
        score.recurse().getElementsByClass(
            stream.Measure
        )
    ):

        if len(m.notes)==0:

            try:
                m.activeSite.remove(m)
            except:
                pass


    print("write")

    score.write(
        "musicxml",
        fp=output_file
    )


    print(
        "DONE",
        output_file
    )



if __name__ == "__main__":

    if len(sys.argv) < 3:

        print(
            "usage: python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit(1)


    clean(
        sys.argv[1],
        sys.argv[2]
    )
