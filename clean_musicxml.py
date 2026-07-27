import sys
import music21
from music21 import stream, note, meter, duration, tie


VERSION = "CLEAN MUSICXML V23.4 FINAL BAR QUANTIZE"


def remove_bad_elements(score):

    print("remove voices")

    for p in score.parts:
        for n in list(p.recurse()):
            
            # remove chord
            if n.classes and "Chord" in n.classes:
                try:
                    n.activeSite.remove(n)
                except:
                    pass


    print("remove beams")

    for n in score.recurse().notes:

        try:
            # 正確移除 beam object
            n.beams = music21.beam.Beams()
        except:
            pass


    print("remove ties")

    for n in score.recurse().notes:

        try:
            n.tie = None
        except:
            pass


    print("remove dots")

    for n in score.recurse().notes:

        try:
            n.duration.dots = 0
        except:
            pass



def quantize_duration(score):

    print("duration quantize")

    allowed = [
        4.0,
        2.0,
        1.0,
        0.5,
        0.25
    ]


    for n in score.recurse().notes:

        q = n.duration.quarterLength

        closest = min(
            allowed,
            key=lambda x:abs(x-q)
        )

        n.duration = duration.Duration(
            closest
        )



def rebuild_measure(score):

    print("force 4/4")

    for p in score.parts:

        p.insert(
            0,
            meter.TimeSignature("4/4")
        )


    print("rebuild measures")

    try:

        score.makeMeasures(
            inPlace=True
        )

    except Exception as e:

        print(
            "makeMeasures skip:",
            e
        )



def split_long_notes(score):

    print("split duration")


    for p in score.parts:

        measures = list(
            p.getElementsByClass(
                stream.Measure
            )
        )


        for m in measures:

            total = 0

            for n in list(m.notes):

                q = n.duration.quarterLength


                if total + q > 4:

                    remain = 4-total


                    if remain > 0:

                        n.duration = duration.Duration(
                            remain
                        )


                    continue


                total += q



def check_measure(score):

    print("check measures")


    for i,m in enumerate(
        score.recurse()
        .getElementsByClass(stream.Measure),
        1
    ):

        length = m.duration.quarterLength

        print(
            "Measure",
            i,
            length
        )


        if length != 4:

            print(
                "WARNING measure",
                i,
                length
            )



def clean_musicxml(
        input_file,
        output_file
):

    print("================")
    print(VERSION)
    print("================")


    print("read")

    score = music21.converter.parse(
        input_file
    )


    remove_bad_elements(score)


    quantize_duration(score)


    rebuild_measure(score)


    split_long_notes(score)


    remove_bad_elements(score)


    check_measure(score)


    print("FINAL WRITE")


    score.write(
        "musicxml",
        fp=output_file
    )


    print()
    print("DONE")
    print(output_file)



if __name__ == "__main__":


    if len(sys.argv)<3:

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit()


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )