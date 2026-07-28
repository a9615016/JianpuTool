# jianpu_fix_musicxml.py V9.0
# FORCE QUANTIZE ALL MEASURES

from music21 import converter, stream, note, meter, duration
import sys


def fix_musicxml(src, dst):

    print("================")
    print("JIANPU FIX MUSICXML V9.0")
    print("================")

    score = converter.parse(src)

    print("remove voices")
    for p in score.parts:
        for el in p.recurse():
            if hasattr(el, "voice"):
                el.voice = None


    print("remove chords")
    for p in score.parts:
        for c in p.recurse().getElementsByClass('Chord'):
            n = c.notes[0]
            c.activeSite.replace(c, n)


    print("force 4/4")
    for p in score.parts:
        p.insert(0, meter.TimeSignature("4/4"))


    print("quantize")

    for p in score.parts:

        notes = list(p.recurse().notesAndRests)

        for n in notes:

            q = n.duration.quarterLength

            # 強制吸附
            if q <= 0.26:
                n.duration.quarterLength = 0.25

            elif q <= 0.75:
                n.duration.quarterLength = 0.5

            elif q <= 1.5:
                n.duration.quarterLength = 1

            elif q <= 3:
                n.duration.quarterLength = 2

            else:
                n.duration.quarterLength = 4


    print("rebuild measures")

    score.makeMeasures(inPlace=True)


    # 第二次修正
    print("check measures")

    for p in score.parts:

        for m in p.getElementsByClass("Measure"):

            length = m.duration.quarterLength

            print(
                "Measure",
                m.number,
                length
            )

            # 超過4拍直接縮短
            if length > 4:

                diff = length - 4

                for n in reversed(
                    list(m.notesAndRests)
                ):

                    if diff <=0:
                        break

                    cut=min(
                        diff,
                        n.duration.quarterLength
                    )

                    n.duration.quarterLength -= cut
                    diff-=cut



    print("FINAL rebuild")

    score.makeMeasures(inPlace=True)


    print("FINAL CHECK")

    ok=True

    for p in score.parts:

        for m in p.getElementsByClass("Measure"):

            x=m.duration.quarterLength

            print(
                "Measure",
                m.number,
                x
            )

            if abs(x-4)>0.001:
                ok=False


    if ok:
        print("ALL MEASURES SAFE")
    else:
        print("WARNING")


    score.write(
        "musicxml",
        fp=dst
    )


    print("DONE")
    print(dst)



if __name__=="__main__":

    fix_musicxml(
        sys.argv[1],
        sys.argv[2]
    )