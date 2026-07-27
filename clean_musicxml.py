# clean_musicxml.py
# CLEAN MUSICXML V21.1

import sys
import copy
from music21 import converter, stream, note, chord, meter


def clean_musicxml(input_file, output_file):

    print("================")
    print("CLEAN MUSICXML V21.1")
    print("================")

    print("input:", input_file)

    print("read")
    score = converter.parse(input_file)


    # =========================
    # remove voices
    # =========================
    print("remove voices")

    for part in score.parts:
        for measure in part.getElementsByClass("Measure"):
            for element in list(measure):

                if hasattr(element, "voice"):
                    element.voice = None



    # =========================
    # remove chords
    # =========================
    print("remove chords")

    for part in score.parts:

        for measure in part.getElementsByClass("Measure"):

            for element in list(measure):

                if isinstance(element, chord.Chord):

                    n = note.Note(
                        element.root()
                    )

                    n.duration = copy.deepcopy(
                        element.duration
                    )

                    measure.replace(
                        element,
                        n
                    )



    # =========================
    # quantize
    # =========================
    print("quantize")

    score.quantize(
        quarterLengthDivisors=[
            4,8,16
        ]
    )



    # =========================
    # force 4/4
    # =========================
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



    # =========================
    # rebuild measures
    # =========================
    print("rebuild measures")


    new_score = stream.Score()


    for part in score.parts:

        new_part = stream.Part()


        for measure in part.getElementsByClass(
            "Measure"
        ):

            new_measure = stream.Measure(
                number=measure.number
            )


            for element in measure:

                # 修正 V21 clone bug
                element3 = copy.deepcopy(element)

                new_measure.append(
                    element3
                )


            new_part.append(
                new_measure
            )


        new_score.append(
            new_part
        )



    # =========================
    # write
    # =========================
    print("write")

    new_score.write(
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