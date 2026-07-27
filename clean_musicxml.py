import music21
import sys


DIVISIONS = 16
BEAT = 4
MEASURE_LENGTH = DIVISIONS * BEAT


def fix_measure_duration(measure):

    total = 0

    for n in list(measure.notesAndRests):
        total += n.duration.quarterLength * DIVISIONS


    # 超過小節長度
    while total > MEASURE_LENGTH:

        for n in list(measure.notesAndRests):

            if n.isNote and n.duration.quarterLength > 0.25:

                old = n.duration.quarterLength

                half = old / 2

                n.duration.quarterLength = half

                new_note = n.clone()
                new_note.duration.quarterLength = half

                measure.insert(
                    n.offset + half,
                    new_note
                )

                total = sum(
                    x.duration.quarterLength * DIVISIONS
                    for x in measure.notesAndRests
                )

                break


    # 不足補休止符
    total = sum(
        x.duration.quarterLength * DIVISIONS
        for x in measure.notesAndRests
    )

    if total < MEASURE_LENGTH:

        rest = music21.note.Rest()

        rest.duration.quarterLength = (
            MEASURE_LENGTH - total
        ) / DIVISIONS

        measure.append(rest)



def clean_musicxml(input_file, output_file):

    print("================")
    print("CLEAN MUSICXML V22.5")
    print("================")

    print("read")

    score = music21.converter.parse(input_file)


    print("remove voices")

    for part in score.parts:
        for measure in part.getElementsByClass(
            music21.stream.Measure
        ):
            measure.voices = []


    print("remove chords")

    for chord in score.recurse().getElementsByClass(
        music21.chord.Chord
    ):

        notes = chord.notes

        for n in notes:
            chord.activeSite.insert(
                chord.offset,
                n
            )

        chord.activeSite.remove(chord)


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
            music21.meter.TimeSignature("4/4")
        )


    print("rebuild measures")

    score.makeMeasures()


    print("split crossing notes")

    for part in score.parts:

        for measure in part.getElementsByClass(
            music21.stream.Measure
        ):

            for n in list(measure.notes):

                if n.duration.quarterLength > 4:

                    pieces = n.splitAtQuarterLength(
                        4
                    )

                    for p in pieces:
                        measure.insert(
                            n.offset,
                            p
                        )

                    measure.remove(n)



    print("FIX measure duration 64")

    for part in score.parts:

        for m in part.getElementsByClass(
            music21.stream.Measure
        ):

            fix_measure_duration(m)


    print("write")

    score.write(
        "musicxml",
        fp=output_file
    )


    print()
    print("DONE", output_file)



if __name__ == "__main__":

    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )