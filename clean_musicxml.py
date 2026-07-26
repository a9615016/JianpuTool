import sys
import music21


def limit_short_notes(value):
    """
    jianpu_ly 不支援過短音符
    最短限制為16分音符
    """

    value = float(value)

    # 16分音符 = 0.25 quarterLength
    minimum = 0.25

    if value < minimum:
        value = minimum

    return value



def clean_musicxml(input_file, output_file):

    print("CLEAN VERSION 20260726 V3")
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


            notes = []


            for voice in voices:

                for n in voice.notesAndRests:

                    notes.append(n)



            measure.removeByClass(
                music21.stream.Voice
            )


            offset = 0


            for n in notes:

                n.offset = offset

                measure.insert(
                    offset,
                    n
                )

                offset += n.quarterLength



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

        note = chord.notes[0]

        note.duration = chord.duration

        chord.activeSite.replace(
            chord,
            note
        )



    # ==========================
    # Remove Grace
    # ==========================

    print("remove grace")


    for n in list(
        score.recurse().notes
    ):

        if n.duration.isGrace:

            n.activeSite.remove(n)



    # ==========================
    # Fix Duration
    # ==========================

    print("fix duration")


    for n in score.recurse().notesAndRests:

        if n.duration.quarterLength <= 0:

            n.duration.quarterLength = 0.25



    # ==========================
    # Disable 128th notes
    # ==========================

    print("limit short notes")


    for n in score.recurse().notesAndRests:

        n.duration.quarterLength = limit_short_notes(
            n.duration.quarterLength
        )



    # ==========================
    # Remove Tuplets
    # ==========================

    print("remove tuplets")


    for n in score.recurse().notesAndRests:

        if n.duration.tuplets:

            ql = limit_short_notes(
                n.duration.quarterLength
            )

            n.duration.clear()

            n.duration.quarterLength = ql



    # ==========================
    # Rebuild Measures
    # ==========================

    print("rebuild measures")


    score.makeMeasures(
        inPlace=True
    )



    # ==========================
    # Final check
    # ==========================

    print("final cleanup")


    for n in score.recurse().notesAndRests:

        n.duration.quarterLength = limit_short_notes(
            n.duration.quarterLength
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