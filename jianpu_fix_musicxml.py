import sys
from music21 import converter, stream, note, chord, meter, clef
from fractions import Fraction


print("================")
print("JIANPU FIX MUSICXML V7.0")
print("FINAL NOTE SPLITTER")
print("================")


INPUT = sys.argv[1]
OUTPUT = sys.argv[2]


print("read:", INPUT)


score = converter.parse(INPUT)


# =========================
# 基本清理
# =========================

print("remove voices")
print("remove chords")
print("remove beams")
print("remove ties")


for part in score.parts:

    # 移除 chord
    for c in list(part.recurse().getElementsByClass('Chord')):
        n = c.sortAscending().notes[-1]
        c.replace(n)


    # 清 tie
    for n in part.recurse().notes:
        n.tie = None


    # 清 beam
    for n in part.recurse().notes:
        try:
            n.beams = []
        except:
            pass



# =========================
# 強制4/4
# =========================

print("force 4/4")


for part in score.parts:

    ts = meter.TimeSignature("4/4")

    part.insert(0, ts)


# =========================
# duration quantize
# =========================


ALLOWED = [
    Fraction(4),
    Fraction(2),
    Fraction(1),
    Fraction(1,2),
    Fraction(1,4),
    Fraction(1,8)
]


def quantize(x):

    best = min(
        ALLOWED,
        key=lambda a: abs(float(a)-float(x))
    )

    return best



print("duration quantize")


for n in score.recurse().notesAndRests:

    q = quantize(Fraction(n.duration.quarterLength))

    n.duration.quarterLength = float(q)



# =========================
# FINAL NOTE SPLITTER
# =========================


print("split notes by measure")


new_score = stream.Score()


for part in score.parts:


    new_part = stream.Part()

    beat = Fraction(0)


    for n in part.recurse().notesAndRests:


        dur = Fraction(
            n.duration.quarterLength
        )


        while dur > 0:


            remain = Fraction(4) - beat


            take = min(
                dur,
                remain
            )


            new_n = n.clone()


            new_n.duration.quarterLength = float(take)


            new_part.append(new_n)


            beat += take
            dur -= take


            if beat >= 4:

                beat = Fraction(0)



    new_score.append(new_part)



score = new_score



# =========================
# 補 metadata
# =========================

for part in score.parts:

    part.insert(
        0,
        clef.TrebleClef()
    )



# =========================
# rebuild measure
# =========================


print("rebuild measures")


score = score.makeMeasures()


# =========================
# FINAL CHECK
# =========================


print("FINAL CHECK")


ok = True


for i,m in enumerate(score.parts[0].measure(1,1000)):

    total = sum(
        Fraction(
            n.duration.quarterLength
        )
        for n in m.notesAndRests
    )

    print(
        "Measure",
        m.number,
        float(total)
    )


    if total != 4:
        ok=False



if ok:
    print("ALL MEASURES SAFE")
else:
    print("WARNING")



# =========================
# write
# =========================


print("FINAL WRITE")


score.write(
    "musicxml",
    fp=OUTPUT
)


print("DONE")
print(OUTPUT)