import sys
import os
import music21
from music21 import note, chord, stream


VERSION = "20260726 V14"


def split_crossing_notes(score):

    print("split crossing notes")

    for part in score.parts:

        new_measures = []

        for m in part.getElementsByClass("Measure"):

            expected = 64
            current = 0

            new_measure = music21.stream.Measure(
                number=m.number
            )

            for element in m.notesAndRests:

                dur = element.duration.quarterLength

                ticks = int(dur * 16)

                # 超過小節容量
                if current + ticks > expected:

                    remain = expected - current

                    if remain > 0 and element.isNote:

                        n1 = element.deepcopy()

                        n1.duration.quarterLength = (
                            remain / 16
                        )

                        new_measure.append(n1)


                    # 建立下一小節
                    overflow = ticks - remain

                    if overflow > 0 and element.isNote:

                        n2 = element.deepcopy()

                        n2.duration.quarterLength = (
                            overflow / 16
                        )

                        # 放入下一小節
                        new_measure.append(n2)


                    current = overflow

                else:

                    new_measure.append(
                        element.deepcopy()
                    )

                    current += ticks


            new_measures.append(
                new_measure
            )


        part.removeByClass(
            "Measure"
        )

        for m in new_measures:
            part.append(m)


    return score



def clean_musicxml(
    input_file,
    output_file
):

    print(
        "CLEAN VERSION",
        VERSION
    )

    print(
        "input:",
        input_file
    )


    score = music21.converter.parse(
        input_file
    )


    print("remove voices")


    # 移除 voice
    for v in score.recurse().getElementsByClass(
        "Voice"
    ):
        v.activeSite.remove(v)



    print("remove chords")


    # chord取最高音
    for c in score.recurse().getElementsByClass(
        "Chord"
    ):

        n = note.Note(
            c.pitches[-1]
        )

        n.duration = c.duration

        c.activeSite.replace(
            c,
            n
        )



    print("remove grace")


    for n in score.recurse().notes:

        if n.duration.isGrace:

            n.duration = music21.duration.Duration(
                0.25
            )



    print("quantize duration")


    for n in score.recurse().notesAndRests:

        q = round(
            n.duration.quarterLength * 16
        ) / 16


        if q <= 0:
            q = 0.25


        n.duration.quarterLength = q



    print("repair measures")


    score.makeMeasures(
        inPlace=True
    )



    print("split crossing notes")


    score = split_crossing_notes(
        score
    )


    print("rebuild measures")


    score.makeMeasures(
        inPlace=True
    )



    print("measure verify")


    for part in score.parts:

        for m in part.getElementsByClass(
            "Measure"
        ):

            length = 0

            for n in m.notesAndRests:

                length += int(
                    n.duration.quarterLength * 16
                )


            print(
                "Measure",
                m.number,
                length
            )


    print("final cleanup")


    score.write(
        "musicxml",
        fp=output_file
    )


    print(
        "done:",
        output_file
    )



if __name__ == "__main__":


    if len(sys.argv) < 2:

        print(
            "usage:"
        )

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit()


    input_file = sys.argv[1]


    if len(sys.argv) >= 3:

        output_file = sys.argv[2]

    else:

        base = os.path.splitext(
            input_file
        )[0]

        output_file = (
            base +
            "_clean.musicxml"
        )


    clean_musicxml(
        input_file,
        output_file
    )