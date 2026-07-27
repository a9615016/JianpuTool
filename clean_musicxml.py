import sys
from music21 import converter, stream, note, chord, meter, tempo


VERSION = "CLEAN MUSICXML V22.2"


def fix_overflow_measures(score):
    """
    修正 4/4 小節超拍問題
    music21 quarterLength:
    4/4 一小節 = 4.0
    """

    print("fix overflow measures")

    for part in score.parts:

        for measure in part.getElementsByClass(stream.Measure):

            total = 0

            elements = list(measure.notesAndRests)

            for element in elements:

                total += element.quarterLength

                # 超過 4 拍
                if total > 4:

                    overflow = total - 4

                    print(
                        "trim:",
                        element,
                        "overflow:",
                        overflow
                    )

                    new_length = element.quarterLength - overflow

                    if new_length > 0:
                        element.quarterLength = new_length

                    else:
                        element.quarterLength = 0.25

                    total = 4


    return score



def clean_musicxml(input_file, output_file):

    print("================")
    print(VERSION)
    print("================")

    print("input:", input_file)

    print("read")

    score = converter.parse(input_file)


    print("remove voices")

    for part in score.parts:
        for n in part.recurse():

            if hasattr(n, "voice"):
                n.voice = None



    print("remove chords")

    for c in score.recurse().getElementsByClass(chord.Chord):

        if len(c.pitches) > 0:

            n = note.Note(c.pitches[0])
            n.duration = c.duration

            c.activeSite.replace(c, n)



    print("quantize")

    for n in score.recurse().notesAndRests:

        q = n.quarterLength

        allowed = [
            0.25,
            0.5,
            1,
            2,
            4
        ]

        closest = min(
            allowed,
            key=lambda x: abs(x-q)
        )

        n.quarterLength = closest



    print("force 4/4")

    for part in score.parts:

        for m in part.getElementsByClass(stream.Measure):

            m.timeSignature = meter.TimeSignature("4/4")



    print("rebuild measures")

    # 重新分小節
    score = score.makeMeasures()



    # V22.2 新增
    score = fix_overflow_measures(score)



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