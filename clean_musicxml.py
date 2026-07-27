import sys
import os
import music21


def fix_measure_duration(score):
    """
    修正每小節拍數
    目標: 4/4 = 4拍
    """

    print("修正 measure duration")

    for part in score.parts:

        measures = list(part.getElementsByClass("Measure"))

        for m in measures:

            total = 0

            for n in m.notesAndRests:
                total += n.duration.quarterLength


            # 4/4 = 4拍
            if total < 4:

                diff = 4 - total

                print(
                    "補休止:",
                    m.number,
                    diff
                )

                r = music21.note.Rest()
                r.duration.quarterLength = diff
                m.append(r)


            elif total > 4:

                print(
                    "超拍:",
                    m.number,
                    total
                )

                # 嘗試縮短最後一個音
                last = m.notesAndRests[-1]

                overflow = total - 4

                new_length = (
                    last.duration.quarterLength
                    - overflow
                )


                if new_length > 0:
                    last.duration.quarterLength = new_length


    return score



def clean(input_file, output_file):

    print("================")
    print("CLEAN MUSICXML")
    print("================")

    print("input:", input_file)


    score = music21.converter.parse(
        input_file
    )


    print("remove voices")

    # 保留第一聲部
    for part in score.parts:

        voices = part.getElementsByClass(
            music21.stream.Voice
        )

        if len(voices):

            first = voices[0]

            part.removeByClass(
                music21.stream.Voice
            )

            for x in first:
                part.append(x)



    print("remove chords")

    for chord in score.recurse().getElementsByClass(
        music21.chord.Chord
    ):

        pitch = chord.sortAscending()[0]

        chord.replace(
            music21.note.Note(pitch)
        )



    print("remove grace")

    for n in score.recurse().notes:

        if n.duration.isGrace:

            n.duration = music21.duration.Duration(
                0.25
            )



    print("force 4/4")

    for m in score.recurse().getElementsByClass(
        music21.stream.Measure
    ):

        m.timeSignature = music21.meter.TimeSignature(
            "4/4"
        )



    print("fix duration")

    score = fix_measure_duration(score)



    print("quantize")


    score.quantize(
        quarterLengthDivisors=[
            1,
            2,
            4,
            8,
            16
        ]
    )


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

    if len(sys.argv) < 2:
        print(
            "usage: python clean_musicxml.py input.musicxml [output.musicxml]"
        )
        sys.exit(1)


    inp = sys.argv[1]


    if len(sys.argv) >= 3:
        out = sys.argv[2]

    else:
        out = os.path.splitext(inp)[0] + "_clean.musicxml"



    clean(
        inp,
        out
    )