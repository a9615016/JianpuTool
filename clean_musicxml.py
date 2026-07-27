import sys
from music21 import converter
from music21 import stream
from music21 import note
from music21 import chord
from music21 import meter
from music21 import duration


VERSION = "CLEAN MUSICXML V22.7 FINAL BAR FIX"


def remove_chords(score):

    print("remove chords")

    for part in score.parts:

        for c in list(
            part.recurse().getElementsByClass(chord.Chord)
        ):

            if len(c.pitches) > 0:

                n = note.Note(
                    c.pitches[-1]
                )

                n.duration = c.duration

                c.activeSite.replace(
                    c,
                    n
                )


def clean_notes(score):

    print("remove ties + beams")

    for n in score.recurse().notes:

        # remove tie
        n.tie = None

        # remove beam
        try:
            n.beams = []
        except:
            pass



def split_crossing_notes(score):

    print("split crossing notes")


    for part in score.parts:

        measures = part.getElementsByClass(
            stream.Measure
        )


        for m in measures:

            new_notes = []


            for n in list(m.notes):

                start = n.offset

                end = (
                    n.offset
                    +
                    n.duration.quarterLength
                )


                # 超過小節
                if end > 4:


                    first = 4 - start


                    if first > 0:


                        n1 = n.clone()

                        n1.duration = duration.Duration(
                            first
                        )


                        n2 = n.clone()

                        n2.offset = 4

                        n2.duration = duration.Duration(
                            end-4
                        )


                        new_notes.append(
                            (n,n1,n2)
                        )



            for old,n1,n2 in new_notes:

                old.activeSite.remove(
                    old
                )

                m.insert(
                    n1.offset,
                    n1
                )

                m.insert(
                    n2.offset,
                    n2
                )



def force_time_signature(score):

    print("force 4/4")


    for part in score.parts:

        ts = part.recurse().getElementsByClass(
            meter.TimeSignature
        )


        if len(ts)==0:

            part.insert(
                0,
                meter.TimeSignature("4/4")
            )



def rebuild(score):

    print("rebuild measures")


    score.makeMeasures(
        inPlace=True
    )



def bar_normalize(score):

    print("bar normalize")


    for part in score.parts:


        for m in part.getElementsByClass(
            stream.Measure
        ):


            total = m.duration.quarterLength


            if total > 4:


                print(
                    "FIX BAR:",
                    m.number,
                    total
                )


                split_crossing_notes(
                    score
                )



def check(score):

    print("check measures")


    for part in score.parts:


        for m in part.getElementsByClass(
            stream.Measure
        ):


            print(
                "Measure",
                m.number,
                m.duration.quarterLength
            )



def clean_musicxml(
        input_file,
        output_file
):


    print("================")
    print(VERSION)
    print("================")


    print("input:",input_file)


    print("read")

    score = converter.parse(
        input_file
    )


    print("remove voices")

    # 不修改 voices
    # music21 voices property 唯讀



    remove_chords(score)


    clean_notes(score)


    print("quantize")

    try:

        score.quantize(
            quarterLengthDivisors=[
                1,
                2,
                4
            ]
        )

    except Exception:

        pass



    force_time_signature(score)


    rebuild(score)


    split_crossing_notes(score)


    bar_normalize(score)


    rebuild(score)


    check(score)


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



if __name__=="__main__":


    if len(sys.argv)<3:

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit()


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )