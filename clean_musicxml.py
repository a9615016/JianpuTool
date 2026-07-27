# CLEAN MUSICXML V18

import sys
from music21 import converter, stream, meter, note, chord

def clean(input_file, output_file):

    print("================")
    print("CLEAN MUSICXML V18")
    print("================")

    print("input:", input_file)

    score = converter.parse(input_file)

    print("remove voices")
    for part in score.parts:
        for n in part.recurse():
            if hasattr(n, "voice"):
                n.voice = None


    print("remove chords")
    for part in score.parts:
        for c in part.recurse().getElementsByClass("Chord"):
            highest = c.pitches[-1]
            new_note = note.Note(
                highest,
                quarterLength=c.duration.quarterLength
            )
            c.activeSite.replace(c, new_note)


    print("quantize")
    score.quantize(
        quarterLengthDivisors=[
            4,8,16
        ]
    )


    print("force 4/4")
    for part in score.parts:
        part.insert(
            0,
            meter.TimeSignature("4/4")
        )


    print("fix measures")

    for part in score.parts:

        measures = part.makeMeasures()

        for m in measures.getElementsByClass("Measure"):

            length = m.duration.quarterLength

            if length > 4:
                print(
                    "trim overflow:",
                    length
                )

                # 重新切小節
                m.duration.quarterLength = 4


        part.coreElementsChanged()


    print("remove empty measures")

    for part in score.parts:
        for m in list(
            part.getElementsByClass("Measure")
        ):
            if len(m.notes)==0:
                part.remove(m)


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

    clean(
        sys.argv[1],
        sys.argv[2]
    )