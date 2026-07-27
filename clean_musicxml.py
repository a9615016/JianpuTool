import sys
import music21


VERSION = "CLEAN MUSICXML V22.6"


def remove_voices(score):

    print("remove voices")

    for part in score.parts:

        for measure in part.getElementsByClass("Measure"):

            voices = list(
                measure.getElementsByClass("Voice")
            )

            for voice in voices:
                for element in list(voice):
                    measure.insert(
                        element.offset,
                        element
                    )

                measure.remove(voice)



def remove_chords(score):

    print("remove chords")

    for part in score.parts:

        for measure in part.getElementsByClass("Measure"):

            for chord in list(
                measure.getElementsByClass("Chord")
            ):

                notes = chord.notes

                measure.remove(chord)

                for n in notes:
                    measure.insert(
                        chord.offset,
                        n
                    )



def quantize(score):

    print("quantize")

    for n in score.recurse().notesAndRests:

        if n.duration.quarterLength <= 0:
            n.duration.quarterLength = 1/4



def force_44(score):

    print("force 4/4")

    for part in score.parts:

        ts = part.recurse().getElementsByClass(
            "TimeSignature"
        )

        if len(ts) == 0:
            part.insert(
                0,
                music21.meter.TimeSignature("4/4")
            )



def rebuild_measures(score):

    print("rebuild measures")

    for part in score.parts:

        part.makeMeasures(
            inPlace=True
        )



def split_crossing_notes(score):

    print("split crossing notes")

    for part in score.parts:

        for measure in part.getElementsByClass(
            "Measure"
        ):

            total = sum(
                n.duration.quarterLength
                for n in measure.notesAndRests
            )

            if total > 4:

                excess = total - 4

                for n in reversed(
                    list(measure.notesAndRests)
                ):

                    if excess <= 0:
                        break

                    if n.duration.quarterLength > excess:

                        n.duration.quarterLength -= excess
                        excess = 0

                    else:

                        excess -= n.duration.quarterLength
                        measure.remove(n)



def normalize_bars(score):

    print("bar normalize")

    for part in score.parts:

        for measure in part.getElementsByClass(
            "Measure"
        ):

            total = sum(
                n.duration.quarterLength
                for n in measure.notesAndRests
            )


            if total < 4:

                rest = music21.note.Rest()

                rest.duration.quarterLength = (
                    4 - total
                )

                measure.append(rest)



def check_measures(score):

    print("check measures")

    for i,m in enumerate(
        score.parts[0].getElementsByClass("Measure")
    ):

        total = sum(
            n.duration.quarterLength
            for n in m.notesAndRests
        )

        print(
            "Measure",
            i+1,
            total
        )



def clean_musicxml(
        input_file,
        output_file
):

    print("================")
    print(VERSION)
    print("================")

    print("input:", input_file)


    print("read")

    score = music21.converter.parse(
        input_file
    )


    remove_voices(score)

    remove_chords(score)

    quantize(score)

    force_44(score)

    rebuild_measures(score)

    split_crossing_notes(score)

    normalize_bars(score)

    check_measures(score)


    print("write")

    score.write(
        "musicxml",
        fp=output_file
    )


    print()
    print(
        "DONE",
        output_file
    )



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