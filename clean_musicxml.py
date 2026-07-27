from music21 import converter, stream, note, chord, meter
import sys


VERSION = "CLEAN MUSICXML V23.8 FINAL BAR QUANTIZE"


def remove_voices(score):

    print("remove voices")

    for part in score.parts:

        voices = list(
            part.getElementsByClass("Voice")
        )

        for v in voices:
            part.remove(v)



def remove_chords(score):

    print("remove chords")

    for c in list(
        score.recurse().getElementsByClass("Chord")
    ):

        try:
            n = note.Note(
                c.pitches[-1]
            )

            n.duration = c.duration

            c.activeSite.replace(
                c,
                n
            )

        except:
            pass



def remove_beams(score):

    print("remove beams")

    for n in score.recurse().notes:

        try:
            n.beams = None
        except:
            pass



def remove_ties(score):

    print("remove ties")

    for n in score.recurse().notes:

        try:
            n.tie = None
        except:
            pass



def force_four_four(score):

    print("force 4/4")

    for part in score.parts:

        part.insert(
            0,
            meter.TimeSignature("4/4")
        )



def split_long_notes(score):

    print("split long notes")

    for n in score.recurse().notes:

        if n.duration.quarterLength > 4:

            n.duration.quarterLength = 4



def measure_check(score):

    print("check measures")

    for part in score.parts:

        for m in list(
            part.getElementsByClass("Measure")
        ):

            print(
                "Measure",
                m.number,
                m.duration.quarterLength
            )



def quantize_bars(score):

    print("bar quantize")


    for part in score.parts:

        measures = list(
            part.getElementsByClass("Measure")
        )


        for m in measures:


            total = m.duration.quarterLength


            if total <= 4:
                continue


            print(
                "fix measure",
                m.number,
                total
            )


            remain = 4


            for n in list(
                m.notesAndRests
            ):


                if remain <= 0:

                    n.duration.quarterLength = 0

                    continue


                dur = n.duration.quarterLength


                if dur > remain:

                    n.duration.quarterLength = remain


                remain -= n.duration.quarterLength



def clean_musicxml(
        input_file,
        output_file
):

    print("================")
    print(VERSION)
    print("================")


    print("read")


    score = converter.parse(
        input_file
    )


    remove_voices(score)

    remove_chords(score)

    remove_beams(score)

    remove_ties(score)

    force_four_four(score)


    split_long_notes(score)


    quantize_bars(score)


    remove_beams(score)

    remove_ties(score)


    measure_check(score)


    print("clear notation cache")


    print("FINAL WRITE")


    score.write(
        "musicxml",
        fp=output_file
    )


    print("DONE")
    print(output_file)



if __name__ == "__main__":


    if len(sys.argv) < 3:

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit(1)


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )