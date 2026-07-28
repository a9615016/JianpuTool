import sys
from music21 import converter, stream, meter, note, chord, duration


print("================")
print("CLEAN MUSICXML V50 BASICPITCH FINAL")
print("================")


if len(sys.argv) < 3:
    print("usage: python clean_musicxml.py input.musicxml output.musicxml")
    sys.exit()


src = sys.argv[1]
out = sys.argv[2]


print("read")

score = converter.parse(src)


# ==========================
# 只保留第一聲部
# ==========================

print("remove extra parts")

if len(score.parts) > 0:
    part = score.parts[0]
else:
    part = score


# ==========================
# 建立新的 Part
# ==========================

new_part = stream.Part()


# 4/4
new_part.append(
    meter.TimeSignature("4/4")
)


print("quantize notes")


# ==========================
# duration quantize
# ==========================

allowed = [
    4.0,
    2.0,
    1.0,
    0.5,
    0.25,
    0.125
]


events = []


for n in part.recurse().notesAndRests:

    # chord取最高音
    if isinstance(n, chord.Chord):
        nn = note.Note(n.pitches[-1])
    else:
        nn = n


    q = float(nn.duration.quarterLength)


    if q <= 0:
        continue


    closest = min(
        allowed,
        key=lambda x: abs(x-q)
    )


    nn.duration = duration.Duration(
        closest
    )


    events.append(nn)



# ==========================
# 重新排小節
# ==========================

print("rebuild measures")


for e in events:
    new_part.append(e)



new_score = stream.Score()

new_score.insert(0,new_part)


# 強制4/4
new_part.makeMeasures(
    inPlace=True
)



# ==========================
# 補滿小節
# ==========================

print("fill rests")


for m in new_part.getElementsByClass("Measure"):

    total = 0

    for n in m.notesAndRests:
        total += n.duration.quarterLength


    diff = 4-total


    if diff > 0.001:

        r = note.Rest()

        r.duration = duration.Duration(diff)

        m.append(r)



# ==========================
# 清除 notation
# ==========================

print("clear notation cache")


for n in new_part.recurse():

    if hasattr(n,"tie"):
        n.tie=None

    if hasattr(n,"beams"):
        try:
            n.beams.fill(0)
        except:
            pass



# ==========================
# 最終檢查
# ==========================

print("FINAL CHECK")


safe=True


for i,m in enumerate(
    new_part.getElementsByClass("Measure"),
    1
):

    length=float(
        m.duration.quarterLength
    )

    print(
        "Measure",
        i,
        length
    )


    if abs(length-4)>0.01:
        safe=False



if safe:
    print("ALL MEASURES SAFE")
else:
    print("WARNING measure mismatch")



print("FINAL WRITE")


new_score.write(
    "musicxml",
    fp=out
)


print("DONE")
print(out)