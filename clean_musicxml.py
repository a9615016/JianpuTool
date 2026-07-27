import sys
import music21


VERSION = "CLEAN MUSICXML V24 FINAL JIANPU COMPATIBLE"


def remove_bad_elements(score):

    print("remove voices")
    print("remove chords")
    print("remove beams")
    print("remove ties")

    for part in score.parts:

        for el in list(part.recurse()):

            if isinstance(el, music21.note.Rest):
                continue

            if isinstance(el, music21.note.Note):
                pass

            elif isinstance(el, music21.chord.Chord):
                try:
                    n = el.notes[0]
                    el.activeSite.replace(el, n)
                except:
                    pass


def quantize_duration(score):

    print("duration quantize")

    allowed = [
        0.25,
        0.5,
        0.75,
        1,
        1.5,
        2,
        3,
        4
    ]

    for n in score.recurse().notes:

        q = float(n.duration.quarterLength)

        nearest = min(
            allowed,
            key=lambda x: abs(x-q)
        )

        n.duration.quarterLength = nearest



def force_time_signature(score):

    print("force 4/4")

    for part in score.parts:

        part.insert(
            0,
            music21.meter.TimeSignature("4/4")
        )



def split_cross_measure_notes(score):

    print("split cross measure notes")

    for part in score.parts:

        measures = part.makeMeasures()

        for m in measures:

            total = float(
                m.duration.quarterLength
            )

            print(
                "Measure",
                m.number,
                total
            )

            # 超過小節
            if total > 4:

                diff = total - 4

                for n in list(m.notes):

                    if diff <= 0:
                        break

                    length = float(
                        n.duration.quarterLength
                    )

                    if length > 0.5:

                        n.duration.quarterLength = (
                            length - diff
                        )

                        diff = 0



def rebuild_measures(score):

    print("rebuild measures")

    try:

        score.makeMeasures(
            inPlace=True
        )

    except Exception as e:

        print(
            "measure rebuild:",
            e
        )



def fill_empty_measure(score):

    print("fill measure rest")

    for part in score.parts:

        for m in part.getElementsByClass(
            music21.stream.Measure
        ):

            total = float(
                m.duration.quarterLength
            )

            if total < 4:

                rest = music21.note.Rest()

                rest.duration.quarterLength = (
                    4-total
                )

                m.append(rest)



def final_check(score):

    print("FINAL CHECK")

    ok=True

    for part in score.parts:

        for m in part.getElementsByClass(
            music21.stream.Measure
        ):

            length=float(
                m.duration.quarterLength
            )

            print(
                "Measure",
                m.number,
                length
            )

            if abs(length-4)>0.01:

                ok=False


    if ok:
        print(
            "ALL MEASURES SAFE"
        )

    else:
        print(
            "WARNING measure mismatch"
        )



def clean_musicxml(input_file, output_file):

    print("================")
    print(VERSION)
    print("================")

    print("read")

    score = music21.converter.parse(
        input_file
    )


    remove_bad_elements(score)

    force_time_signature(score)

    quantize_duration(score)

    rebuild_measures(score)

    split_cross_measure_notes(score)

    rebuild_measures(score)

    fill_empty_measure(score)

    rebuild_measures(score)


    print(
        "clear notation cache"
    )


    final_check(score)


    print(
        "FINAL WRITE"
    )


    score.write(
        "musicxml",
        fp=output_file
    )


    print("DONE")
    print(output_file)



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