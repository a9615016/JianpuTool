import sys
import music21


def quantize_length(value):
    """
    量化到 1/4 拍
    """
    value = float(value)

    value = round(value * 4) / 4

    if value <= 0:
        value = 0.25

    return value



def clean_musicxml(input_file, output_file):

    print("CLEAN VERSION 20260726 V2")
    print("input:", input_file)


    score = music21.converter.parse(input_file)



    # ==========================
    # Remove Voices
    # ==========================

    print("remove voices")


    for part in score.parts:

        for measure in part.getElementsByClass(
            music21.stream.Measure
        ):

            voices = list(
                measure.getElementsByClass(
                    music21.stream.Voice
                )
            )


            if not voices:
                continue


            elements = []


            for voice in voices:

                for e in voice.notesAndRests:

                    elements.append(e)



            measure.removeByClass(
                music21.stream.Voice
            )


            offset = 0


            for e in elements:

                e.offset = offset

                measure.insert(
                    offset,
                    e
                )

                offset += e.quarterLength



    # ==========================
    # Remove Chords
    # ==========================

    print("remove chords")


    for chord in list(
        score.recurse()
        .getElementsByClass(
            music21.chord.Chord
        )
    ):

        note = chord.notes[-1]

        note.duration = chord.duration

        chord.activeSite.replace(
            chord,
            note
        )



    # ==========================
    # Remove Grace Notes
    # ==========================

    print("remove grace notes")


    for n in list(
        score.recurse()
        .notes
    ):

        if n.duration.isGrace:

            n.activeSite.remove(n)



    # ==========================
    # Quantize
    # ==========================

    print("quantize duration")


    for n in score.recurse().notesAndRests:

        n.duration.quarterLength = quantize_length(
            n.duration.quarterLength
        )



    # ==========================
    # Remove Tuplets
    # ==========================

    print("remove tuplets")


    for n in score.recurse().notesAndRests:

        if n.duration.tuplets:

            ql = quantize_length(
                n.duration.quarterLength
            )

            n.duration.clear()

            n.duration.quarterLength = ql



    # ==========================
    # Fix Measure Duration
    # ==========================

    print("fix measure duration")


    for part in score.parts:


        for measure in part.getElementsByClass(
            music21.stream.Measure
        ):


            expected = float(
                measure.barDuration.quarterLength
            )


            elements = list(
                measure.notesAndRests
            )


            total = sum(
                float(e.duration.quarterLength)
                for e in elements
            )


            diff = expected - total



            # 少拍補 Rest
            if diff > 0.01:


                rest = music21.note.Rest()


                rest.duration.quarterLength = quantize_length(
                    diff
                )


                measure.append(rest)



            # 超拍修正最後元素
            elif diff < -0.01:


                print(
                    "shorten measure:",
                    measure.number,
                    total,
                    expected
                )


                for e in reversed(elements):


                    new_value = (
                        float(e.duration.quarterLength)
                        + diff
                    )


                    new_value = quantize_length(
                        new_value
                    )


                    if new_value > 0:

                        e.duration.quarterLength = new_value

                        break



    # ==========================
    # Final Duration Check
    # ==========================

    print("final duration check")


    for n in score.recurse().notesAndRests:

        n.duration.quarterLength = quantize_length(
            n.duration.quarterLength
        )



    # ==========================
    # Rebuild Measures
    # ==========================

    print("final cleanup")


    score.makeMeasures(
        inPlace=True
    )



    # ==========================
    # Write
    # ==========================

    print("write")


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
            "Usage:"
        )

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit(1)



    input_file = sys.argv[1]


    if len(sys.argv) >= 3:

        output_file = sys.argv[2]

    else:

        output_file = input_file.replace(
            ".musicxml",
            "_clean.musicxml"
        )


    clean_musicxml(
        input_file,
        output_file
    )