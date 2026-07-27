import sys
import music21
from music21 import chord, note, stream


VERSION = "CLEAN MUSICXML V22.3"


def clean_musicxml(input_file, output_file):

    print("================")
    print(VERSION)
    print("================")

    print("input:", input_file)

    score = music21.converter.parse(input_file)

    print("read")


    # =========================
    # remove voices
    # =========================
    print("remove voices")

    for part in score.parts:
        for n in part.recurse():
            if hasattr(n, "voice"):
                n.voice = None



    # =========================
    # remove chords
    # =========================
    print("remove chords")

    for part in score.parts:

        elements = list(part.recurse())

        for c in elements:

            if isinstance(c, chord.Chord):

                if len(c.notes) > 0:

                    # 取最高音
                    highest = max(
                        c.notes,
                        key=lambda x: x.pitch.midi
                    )

                    new_note = note.Note(
                        highest.pitch
                    )

                    new_note.duration = c.duration

                    try:
                        c.activeSite.replace(
                            c,
                            new_note
                        )
                    except Exception:
                        pass



    # =========================
    # quantize
    # =========================
    print("quantize")

    try:
        score.quantize(
            quarterLengthDivisors=[
                1,2,4,8,16
            ],
            processOffsets=True,
            processDurations=True
        )
    except Exception:
        pass



    # =========================
    # force 4/4
    # =========================
    print("force 4/4")

    for part in score.parts:

        part.insert(
            0,
            music21.meter.TimeSignature("4/4")
        )



    # =========================
    # rebuild measures
    # =========================
    print("rebuild measures")

    try:
        score.makeMeasures(
            inPlace=True
        )
    except Exception:
        pass



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
            "python clean_musicxml.py input.musicxml output.musicxml"
        )
        sys.exit()


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )