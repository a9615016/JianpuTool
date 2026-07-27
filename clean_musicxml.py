import sys
import music21
from music21 import stream, note, chord, duration


print("================")
print("CLEAN MUSICXML V23.2 FINAL INDENT + DURATION SAFE")
print("================")


def remove_voices(score):
    print("remove voices")
    for part in score.parts:
        for el in list(part.recurse()):
            if hasattr(el, "voice"):
                try:
                    el.voice = None
                except:
                    pass


def remove_chords(score):
    print("remove chords")
    for part in score.parts:
        for c in list(part.recurse().getElementsByClass("Chord")):
            n = note.Note(c.root())
            n.duration = c.duration
            part.replace(c, n)


def remove_bad_duration(score):
    print("duration safe")

    for n in score.recurse().notesAndRests:

        q = n.duration.quarterLength

        # 太短全部升級
        if q < 0.25:
            print("fix duration:", q)

            n.duration = duration.Duration(0.25)


def reset_beams(score):

    print("safe beam reset")

    for n in score.recurse().notes:

        try:
            n.beams = None
        except:
            pass



def quantize(score):

    print("quantize")

    for n in score.recurse().notesAndRests:

        q = n.duration.quarterLength

        allowed=[
            4,
            2,
            1,
            0.5,
            0.25
        ]

        closest=min(
            allowed,
            key=lambda x:abs(x-q)
        )

        n.duration.quarterLength=closest



def force_44(score):

    print("force 4/4")

    for part in score.parts:

        part.insert(
            0,
            music21.meter.TimeSignature("4/4")
        )



def rebuild(score):

    print("rebuild measures")

    score.makeMeasures(
        inPlace=True
    )


def check(score):

    print("check measures")

    for i,m in enumerate(score.recurse().getElementsByClass("Measure")):

        length=m.barDuration.quarterLength

        print(
            "Measure",
            i+1,
            length
        )


def clean_musicxml(inp,out):

    print("read")

    score=music21.converter.parse(inp)


    remove_voices(score)

    remove_chords(score)

    reset_beams(score)

    quantize(score)

    remove_bad_duration(score)

    force_44(score)

    rebuild(score)

    reset_beams(score)

    check(score)


    print("write")

    score.write(
        "musicxml",
        fp=out
    )


    print()
    print("DONE",out)



if __name__=="__main__":

    if len(sys.argv)<3:
        print(
            "usage: python clean_musicxml.py input.musicxml output.musicxml"
        )
        sys.exit()


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )