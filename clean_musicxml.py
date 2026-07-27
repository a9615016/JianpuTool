from music21 import converter, stream, note, chord, meter
import sys


VERSION = "CLEAN MUSICXML V23.7 FIX STREAMITERATOR"


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

    for part in score.parts:

        chords = list(
            part.recurse().getElementsByClass("Chord")
        )

        for c in chords:

            n = note.Note(
                c.pitches[-1]
            )

            n.duration = c.duration

            c.activeSite.replace(
                c,
                n
            )



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

    ts = meter.TimeSignature("4/4")

    for part in score.parts:

        part.insert(
            0,
            ts
        )



def split_long_notes(score):

    print("split long notes")

    for n in score.recurse().notes:

        if n.duration.quarterLength > 4:

            n.duration.quarterLength = 4



def split_long_measures(score):

    print("measure split")

    for part in score.parts:

        # 重要：轉 list，避免 StreamIterator
        measures = list(
            part.getElementsByClass("Measure")
        )


        for m in measures:

            ql = m.duration.quarterLength

            print(
                "Measure",
                m.number,
                ql
            )


            # 正常小節跳過
            if ql <= 4:
                continue


            print(
                "split long measure:",
                m.number
            )


            notes = list(
                m.notesAndRests
            )


            # 建立新小節
            new_measure = stream.Measure(
                number=str(m.number) + ".5"
            )


            for n in notes:

                if n.offset >= 4:

                    n.offset -= 4

                    new_measure.insert(
                        n.offset,
                        n
                    )


            # 正確移除 Music21Object
            part.remove(
                m
            )


            # 放回原小節
            part.insert(
                m.offset,
                m
            )


            if len(
                list(new_measure.notesAndRests)
            ) > 0:

                part.insert(
                    m.offset + 4,
                    new_measure
                )



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


    split_long_measures(score)

    split_long_notes(score)


    remove_beams(score)

    remove_ties(score)


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