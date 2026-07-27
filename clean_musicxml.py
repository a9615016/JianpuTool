import sys
from music21 import converter, stream, note, chord, meter, beam


VERSION = "CLEAN MUSICXML V25 FINAL TICK LOCK"


TICK_MAP = [
    (4.0, 64),   # whole
    (2.0, 32),   # half
    (1.0, 16),   # quarter
    (0.5, 8),    # eighth
    (0.25, 4),   # sixteenth
]


def quantize_duration(q):
    """
    quarterLength -> tick lock
    divisions=16
    """

    ticks = round(q * 16)

    candidates = [
        64,
        48,
        32,
        24,
        16,
        12,
        8,
        6,
        4,
        2,
        1
    ]

    best = min(
        candidates,
        key=lambda x: abs(x - ticks)
    )

    return best / 16



def remove_bad_elements(score):

    print("remove voices")

    for part in score.parts:

        for v in list(part.voices):

            try:
                part.remove(v)
            except:
                pass


    print("remove chords")

    for c in score.recurse().getElementsByClass(chord.Chord):

        n = note.Note(
            c.root()
        )

        n.duration = c.duration

        c.activeSite.replace(
            c,
            n
        )


    print("remove beams")

    for b in score.recurse().getElementsByClass(
        beam.Beams
    ):
        try:
            b.clear()
        except:
            pass



def force_4_4(score):

    print("force 4/4")

    for part in score.parts:

        part.insert(
            0,
            meter.TimeSignature("4/4")
        )



def tick_lock(score):

    print("TICK LOCK")

    for n in score.recurse().notes:

        old = n.duration.quarterLength

        new = quantize_duration(
            old
        )

        n.duration.quarterLength = new



def rebuild_measures(score):

    print("rebuild measures")

    for part in score.parts:

        part.makeMeasures(
            inPlace=True
        )



def check_bars(score):

    print("FINAL BAR CHECK")

    for part in score.parts:

        for i,m in enumerate(part.getElementsByClass("Measure"),1):

            length = round(
                m.duration.quarterLength,
                4
            )

            print(
                "Measure",
                i,
                length
            )

            if length > 4.0001:

                print(
                    "WARNING BAR OVER"
                )



def set_divisions(score):

    print("set divisions 16")

    score.metadata = score.metadata

    for part in score.parts:

        for m in part.getElementsByClass("Measure"):

            m.editorial.divisions = 16



def clean_musicxml(
    input_file,
    output_file
):

    print("================")
    print(VERSION)
    print("================")


    print("read")

    score = converter.parse(
        input_file
    )


    remove_bad_elements(score)


    force_4_4(score)


    tick_lock(score)


    rebuild_measures(score)


    set_divisions(score)


    check_bars(score)


    print("FINAL WRITE")


    score.write(
        "musicxml",
        fp=output_file
    )


    print("DONE")
    print(output_file)



if __name__ == "__main__":

    if len(sys.argv) < 3:

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit()


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )