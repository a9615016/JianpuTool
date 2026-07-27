import sys
import music21
from music21 import beam


VERSION = "CLEAN MUSICXML V23.3.4 FINAL NO BEAM REBUILD"


def remove_voices(score):
    print("remove voices")

    for p in score.parts:
        for n in p.recurse().notes:
            try:
                n.voice = None
            except:
                pass



def remove_chords(score):
    print("remove chords")

    for c in list(score.recurse().getElementsByClass("Chord")):
        try:
            if len(c.notes) > 0:
                c.replace(c.notes[0])
        except:
            pass



def remove_beams(score):

    print("remove beams")

    for n in score.recurse().notes:

        try:
            # music21 正確 Beam 物件
            n.beams = beam.Beams()

        except:
            pass



def remove_ties(score):

    print("remove ties")

    for n in score.recurse().notes:

        try:
            n.tie = None

        except:
            pass



def remove_dots(score):

    print("remove dots")

    for n in score.recurse().notes:

        try:
            n.duration.dots = 0

        except:
            pass



def duration_safe(score):

    print("duration safe")

    for n in score.recurse().notes:

        try:

            ql = n.duration.quarterLength

            if ql <= 0:

                n.duration.quarterLength = 0.25


        except:

            pass



def force_44(score):

    print("force 4/4")

    for p in score.parts:

        try:

            p.insert(
                0,
                music21.meter.TimeSignature("4/4")
            )

        except:

            pass



def rebuild_measures(score):

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



def check_measures(score):

    print("check measures")

    try:

        for i,m in enumerate(
            score.parts[0]
            .getElementsByClass("Measure")
        ):

            print(
                "Measure",
                i+1,
                m.duration.quarterLength
            )

    except Exception as e:

        print(
            "measure check error:",
            e
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


    remove_voices(score)

    remove_chords(score)

    remove_beams(score)

    remove_ties(score)

    remove_dots(score)

    duration_safe(score)

    force_44(score)

    rebuild_measures(score)


    # 最後保險
    remove_beams(score)

    remove_ties(score)


    check_measures(score)


    print("write")


    # 注意:
    # 不呼叫 makeNotation
    # 避免 beamsList 錯誤

    score.write(
        "musicxml",
        fp=output_file
    )


    print()
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