# clean_musicxml.py
# V60
# jianpu_ly 專用硬相容版
#
# fix:
# - flatten score
# - remove voices
# - remove notation
# - strict quantize
# - rebuild 4/4 measures


from music21 import converter, stream, note, meter, tempo
import sys
import copy
from fractions import Fraction


VERSION = "CLEAN MUSICXML V60"


# jianpu_ly 最穩定單位
# 四分音符 = 1
# 最小 1/16

GRID = [
    Fraction(4,1),
    Fraction(2,1),
    Fraction(1,1),
    Fraction(1,2),
    Fraction(1,4)
]


def nearest_duration(x):

    x = Fraction(x)

    return min(
        GRID,
        key=lambda y: abs(x-y)
    )



def remove_notation(score):

    for n in score.recurse().notes:

        n.tie = None

        try:
            n.beams = []
        except:
            pass

        n.articulations = []
        n.expressions = []


    return score



def remove_tempo(score):

    for t in list(
        score.recurse()
        .getElementsByClass(tempo.MetronomeMark)
    ):

        if t.activeSite:
            t.activeSite.remove(t)

    return score



def collect_events(part):

    """
    flatten + offset 排序
    """

    flat = part.flatten()

    events = list(
        flat.notesAndRests
    )


    events.sort(
        key=lambda x:x.offset
    )


    return events



def rebuild_part(part):


    events = collect_events(part)


    new_part = stream.Part()


    measure_no = 1


    measure = stream.Measure(
        number=measure_no
    )


    measure.insert(
        0,
        meter.TimeSignature("4/4")
    )


    pos = Fraction(0)


    for item in events:


        dur = nearest_duration(
            item.duration.quarterLength
        )


        while dur > 0:


            remain = Fraction(4)-pos


            take=min(
                dur,
                remain
            )


            new = copy.deepcopy(item)


            new.duration.quarterLength = take


            new.tie = None


            measure.append(new)


            pos += take

            dur -= take



            if pos >= 4:


                new_part.append(
                    measure
                )


                measure_no += 1


                measure = stream.Measure(
                    number=measure_no
                )


                measure.insert(
                    0,
                    meter.TimeSignature("4/4")
                )


                pos = Fraction(0)



    # 補最後小節

    if len(measure.notesAndRests):


        while pos < 4:


            r = note.Rest()


            r.duration.quarterLength = min(
                Fraction(1),
                Fraction(4)-pos
            )


            measure.append(r)


            pos += r.duration.quarterLength



        new_part.append(
            measure
        )


    return new_part



def final_check(score):


    print("V60 FINAL CHECK")


    for i,m in enumerate(
        score.parts[0]
        .getElementsByClass(stream.Measure),
        1
    ):


        total=sum(
            Fraction(x.duration.quarterLength)
            for x in m.notesAndRests
        )


        print(
            "Measure",
            i,
            float(total)
        )


        if total != 4:

            print(
                "WARNING",
                i,
                total
            )



def clean(inp,out):


    print(VERSION)


    score = converter.parse(inp)


    score = remove_tempo(score)

    score = remove_notation(score)



    new_score = stream.Score()



    for part in score.parts:


        new_part = rebuild_part(part)


        new_score.append(
            new_part
        )



    final_check(
        new_score
    )


    print("FINAL WRITE")


    new_score.write(
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


    clean(
        inp,
        out
    )