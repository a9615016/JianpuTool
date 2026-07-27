import sys
import music21
from music21 import stream


VERSION = "CLEAN MUSICXML V23.3.3 FINAL NO BEAM OBJECT"


def remove_voices(score):
    print("remove voices")
    for p in score.parts:
        for n in p.recurse().notes:
            if hasattr(n, "voice"):
                n.voice = None


def remove_chords(score):
    print("remove chords")
    for p in score.parts:
        for c in list(p.recurse().getElementsByClass("Chord")):
            try:
                n = c.notes[0]
                c.replace(n)
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
            if n.duration.quarterLength <= 0:
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
        score.makeMeasures(inPlace=True)
    except Exception as e:
        print("makeMeasures skip:", e)



def check_measure(score):

    print("check measures")

    for i,m in enumerate(score.parts[0].getElementsByClass("Measure")):

        try:
            print(
                "Measure",
                i+1,
                m.duration.quarterLength
            )

        except:
            pass



def clean_musicxml(input_file, output_file):

    print("================")
    print(VERSION)
    print("================")


    print("read")

    score = music21.converter.parse(input_file)


    remove_voices(score)

    remove_chords(score)

    remove_beams(score)

    remove_ties(score)

    remove_dots(score)

    duration_safe(score)

    force_44(score)

    rebuild_measures(score)


    # 最後一次保險
    remove_beams(score)
    remove_ties(score)


    check_measure(score)


    print("FINAL WRITE")


    # 關閉 music21 自動 notation
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
        sys.exit()


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )