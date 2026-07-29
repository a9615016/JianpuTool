print("========== USING V42 ==========")
# clean_musicxml.py
# V42
# jianpu_ly strict compatible rebuild

from music21 import converter, stream, note, meter, tempo
from fractions import Fraction
import copy
import sys


VERSION = "CLEAN MUSICXML V42"


TICK = 16          # divisions
BAR = 64           # 4/4


def clean_note(n):

    n2 = copy.deepcopy(n)

    n2.tie = None

    if hasattr(n2, "beams"):
        n2.beams.clear()

    if hasattr(n2, "articulations"):
        n2.articulations = []

    if hasattr(n2, "expressions"):
        n2.expressions = []

    return n2



def quantize_duration(q):

    ticks = round(
        float(q) * TICK
    )

    if ticks <= 0:
        ticks = 4

    return ticks



def rebuild_part(part):

    new_part = stream.Part()

    new_part.append(
        meter.TimeSignature("4/4")
    )


    measure = stream.Measure(number=1)

    used = 0


    # 注意：
    # 不使用 notesAndRests
    # 只重新建立音符
    for n in part.recurse().notes:

        remain_ticks = quantize_duration(
            n.duration.quarterLength
        )


        while remain_ticks > 0:

            free = BAR - used

            take = min(
                free,
                remain_ticks
            )


            nn = clean_note(n)

            nn.duration.quarterLength = Fraction(
                take,
                TICK
            )


            measure.append(nn)


            used += take
            remain_ticks -= take


            if used == BAR:

                new_part.append(measure)

                measure = stream.Measure(
                    number=len(
                        new_part.getElementsByClass(
                            stream.Measure
                        )
                    ) + 1
                )

                used = 0



    # 補最後小節
    if used > 0:

        while used < BAR:

            r = note.Rest()

            r.duration.quarterLength = Fraction(
                min(4, BAR-used),
                TICK
            )

            measure.append(r)

            used += min(
                4,
                BAR-used
            )


        new_part.append(measure)



    return new_part



def force_44(score):

    for p in score.parts:

        p.insert(
            0,
            meter.TimeSignature("4/4")
        )

    return score



def final_check(score):

    print("V42 FINAL CHECK")


    for i,m in enumerate(
        score.parts[0].getElementsByClass(stream.Measure),
        1
    ):

        total = sum(
            x.duration.quarterLength
            for x in m.notesAndRests
        )

        print(
            "Measure",
            i,
            float(total)
        )



def clean(inp,out):

    print(VERSION)


    src = converter.parse(inp)


    # 移除 tempo
    for t in src.recurse().getElementsByClass(
        tempo.MetronomeMark
    ):
        t.activeSite.remove(t)



    dst = stream.Score()


    for part in src.parts:

        print("REBUILD STRICT PART")

        dst.append(
            rebuild_part(part)
        )


    force_44(dst)


    final_check(dst)


    print("FINAL WRITE")


    dst.write(
        "musicxml",
        fp=out
    )


    print("DONE")
    print(out)



if __name__=="__main__":

    inp=sys.argv[1]

    out="clean.musicxml"

    if len(sys.argv)>2:
        out=sys.argv[2]


    clean(inp,out)