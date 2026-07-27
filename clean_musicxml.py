import sys
import music21
import os


print("================")
print("CLEAN MUSICXML")
print("================")


def quantize_duration(q):
    """
    將 duration 限制到 jianpu_ly 支援範圍
    """

    allowed = [
        0.25,   # 16分音符
        0.5,    # 8分音符
        0.75,
        1,
        1.5,
        2,
        3,
        4
    ]

    return min(
        allowed,
        key=lambda x: abs(x - q)
    )


def clean(input_file, output_file):

    print("input:", input_file)


    score = music21.converter.parse(input_file)


    print("remove voices")

    for part in score.parts:

        for measure in part.getElementsByClass(
            music21.stream.Measure
        ):

            for v in list(
                measure.getElementsByClass(
                    music21.stream.Voice
                )
            ):
                v.remove()


    print("remove chords")


    for part in score.parts:

        for measure in part.getElementsByClass(
            music21.stream.Measure
        ):

            for element in list(measure.notes):

                if isinstance(
                    element,
                    music21.chord.Chord
                ):

                    # 取最高音
                    note = element.notes[-1]

                    element.replace(
                        element,
                        note
                    )


    print("quantize")


    for note in score.recurse().notesAndRests:

        q = note.duration.quarterLength

        new_q = quantize_duration(q)

        note.duration.quarterLength = new_q



    print("force 4/4")


    for part in score.parts:

        for measure in part.getElementsByClass(
            music21.stream.Measure
        ):

            measure.timeSignature = (
                music21.meter.TimeSignature("4/4")
            )


    print("fix duration")


    for part in score.parts:

        total = 0

        for measure in part.getElementsByClass(
            music21.stream.Measure
        ):

            length = 0

            for n in measure.notesAndRests:

                length += n.duration.quarterLength


            # 超過4拍，縮短最後音符
            if length > 4:

                diff = length - 4

                elems = list(
                    measure.notesAndRests
                )

                if elems:

                    last = elems[-1]

                    new_len = (
                        last.duration.quarterLength
                        - diff
                    )

                    if new_len > 0:

                        last.duration.quarterLength = new_len



    print("remove empty measures")


    for part in score.parts:

        for m in list(
            part.getElementsByClass(
                music21.stream.Measure
            )
        ):

            if len(m.notesAndRests) == 0:

                part.remove(m)



    print("write")


    score.write(
        "musicxml",
        fp=output_file
    )


    print("DONE", output_file)



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
