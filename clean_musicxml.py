import sys
import music21


def quantize_length(value):

    value = float(value)

    # 量化到 1/16 拍
    value = round(value * 4) / 4

    if value <= 0:
        value = 0.25

    return value



def clean_musicxml(input_file, output_file):

    print("CLEAN VERSION 20260726 V3")
    print("input:", input_file)


    score = music21.converter.parse(input_file)


    # ==========================
    # Keep first part only
    # ==========================

    print("keep first part only")


    if len(score.parts) > 1:

        score = music21.stream.Score(
            score.parts[0]
        )



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


            for voice in voices:

                for e in voice.notesAndRests:

                    measure.insert(
                        e.offset,
                        e
                    )


                measure.remove(
                    voice
                )



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
    # Quantize duration
    # ==========================

    print("quantize duration")


    for n in score.recurse().notesAndRests:

        ql = quantize_length(
            n.duration.quarterLength
        )

        n.duration.clear()

        n.duration.quarterLength = ql



    # ==========================
    # Remove tuplets
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
    # Rebuild measures
    # ==========================

    print("rebuild measures")


    score = score.makeMeasures(
        inPlace=False
    )



    # ==========================
    # Fix measure duration
    # ==========================

    print("fix measure duration")


    for part in score.parts:

        for measure in part.getElementsByClass(
            music21.stream.Measure
        ):

            expected = float(
                measure.barDuration.quarterLength
            )


            total = sum(
                float(x.duration.quarterLength)
                for x in measure.notesAndRests
            )


            diff = expected - total


            if diff > 0.01:

                rest = music21.note.Rest()

                rest.duration.quarterLength = quantize_length(
                    diff
                )

                measure.append(rest)



    # ==========================
    # Final export safety
    # ==========================

    print("export safety")


    for n in score.recurse().notesAndRests:

        ql = quantize_length(
            n.duration.quarterLength
        )

        n.duration.clear()

        n.duration.quarterLength = ql



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