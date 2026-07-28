from music21 import converter, note, stream, meter
import sys


print("================")
print("CLEAN MUSICXML V25 FINAL JIANPU FIX")
print("================")


if len(sys.argv) < 3:
    print(
        "usage: python clean_musicxml.py input.musicxml output.musicxml"
    )
    sys.exit()


src = sys.argv[1]
dst = sys.argv[2]


print("read")

score = converter.parse(src)



# ==========================
# 清理
# ==========================

print("remove voices")

for part in score.parts:

    for el in list(part.recurse()):

        if hasattr(el, "voice"):
            try:
                el.voice = None
            except:
                pass



print("remove chords")

for part in score.parts:

    for c in list(part.recurse().getElementsByClass("Chord")):

        n = note.Note(
            c.pitches[0]
        )

        n.duration = c.duration

        c.activeSite.replace(
            c,
            n
        )



print("remove beams")

for n in score.recurse().notes:

    try:
        n.beams = []
    except:
        pass



print("remove ties")

for n in score.recurse().notes:

    try:
        n.tie = None
    except:
        pass



# ==========================
# 4/4
# ==========================

print("force 4/4")


for part in score.parts:

    part.insert(
        0,
        meter.TimeSignature("4/4")
    )



# ==========================
# duration quantize
# ==========================

print("duration quantize")


for n in score.recurse().notesAndRests:

    q = float(n.duration.quarterLength)

    # 16分音符
    q = round(q * 4) / 4

    if q <= 0:
        q = 0.25


    n.duration.quarterLength = q



# ==========================
# rebuild measures
# ==========================

print("rebuild measures")


for part in score.parts:

    part.makeMeasures(
        inPlace=True
    )



# ==========================
# 修正超拍小節
# ==========================

print("fix measure length")


for part in score.parts:


    for m in part.getElementsByClass("Measure"):


        total = float(
            m.duration.quarterLength
        )


        print(
            "Measure",
            m.number,
            total
        )


        while total > 4:


            elems = list(
                m.notesAndRests
            )


            if not elems:
                break


            last = elems[-1]


            if isinstance(last, note.Note):

                old = float(
                    last.duration.quarterLength
                )


                last.duration.quarterLength = max(
                    0.25,
                    old - 0.25
                )

            else:

                break


            total = float(
                m.duration.quarterLength
            )



        if total < 4:


            r = note.Rest()

            r.duration.quarterLength = (
                4-total
            )

            m.append(r)



# ==========================
# rebuild again
# ==========================

print("rebuild measures again")


for part in score.parts:

    part.makeMeasures(
        inPlace=True
    )



score.clearCache()



# ==========================
# FINAL CHECK
# ==========================

print("================")
print("FINAL CHECK")
print("================")


bad = False


for part in score.parts:

    for m in part.getElementsByClass("Measure"):

        q = float(
            m.duration.quarterLength
        )


        print(
            "Measure",
            m.number,
            q
        )


        if abs(q-4.0) > 0.01:

            bad = True



if bad:

    print(
        "WARNING measure mismatch"
    )

else:

    print(
        "ALL MEASURES SAFE"
    )



print("FINAL WRITE")


score.write(
    "musicxml",
    fp=dst
)


print("DONE")
print(dst)