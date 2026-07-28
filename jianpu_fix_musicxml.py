# ==========================================
# jianpu_fix_musicxml.py V10.0
# FORCE SPLIT + QUANTIZE FOR JIANPU_LY
# ==========================================

from music21 import converter, meter, note, stream, chord
import sys


def quantize_length(x):

    table = [
        (0.25, 0.25),
        (0.333, 0.25),
        (0.5, 0.5),
        (0.666, 0.5),
        (0.75, 0.75),
        (1.0, 1.0),
        (1.333, 1.25),
        (1.5, 1.5),
        (2.0, 2.0),
        (3.0, 3.0),
        (4.0, 4.0),
    ]

    for a,b in table:
        if abs(x-a)<0.05:
            return b

    if x < 0.25:
        return 0.25

    if x > 4:
        return 4

    return round(x*4)/4



def remove_bad_elements(score):

    print("remove ties beams voices")

    for el in score.recurse():

        if hasattr(el,"tie"):
            el.tie=None

        if hasattr(el,"beams"):
            try:
                el.beams.clear()
            except:
                pass

        if hasattr(el,"voice"):
            el.voice=None



def fix_notes(score):

    print("duration quantize")

    for n in score.recurse().notesAndRests:

        q=n.duration.quarterLength

        nq=quantize_length(q)

        n.duration.quarterLength=nq



def rebuild(score):

    print("rebuild measures")

    for p in score.parts:

        p.makeMeasures(inPlace=True)



def check(score):

    print("FINAL CHECK")

    ok=True

    for p in score.parts:

        for m in p.getElementsByClass("Measure"):

            q=m.duration.quarterLength

            print(
                "Measure",
                m.number,
                q
            )

            if abs(q-4)>0.01:
                ok=False


    if ok:
        print("ALL MEASURES SAFE")
    else:
        print("WARNING measure mismatch")


    return ok



def fix(src,dst):

    print("================")
    print("JIANPU FIX V10")
    print("================")

    score=converter.parse(src)


    print("force 4/4")

    for p in score.parts:
        p.insert(
            0,
            meter.TimeSignature("4/4")
        )


    remove_bad_elements(score)

    fix_notes(score)

    rebuild(score)


    # 第二輪
    fix_notes(score)

    rebuild(score)


    check(score)


    print("FINAL WRITE")

    score.write(
        "musicxml",
        fp=dst
    )


    print("DONE")
    print(dst)



if __name__=="__main__":

    fix(
        sys.argv[1],
        sys.argv[2]
    )