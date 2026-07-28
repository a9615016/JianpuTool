from music21 import converter, note, stream, meter
import sys


print("================")
print("CLEAN MUSICXML V25 JIANPU FIX")
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



# =========================
# remove voices
# =========================

print("remove voices")

for part in score.parts:

    for n in part.recurse():

        if hasattr(n, "voice"):
            try:
                n.voice = None
            except:
                pass



# =========================
# remove chords
# =========================

print("remove chords")

for part in score.parts:

    for c in list(part.recurse().getElementsByClass("Chord")):

        highest = c.notes[-1]

        new = note.Note(
            highest.pitch
        )

        new.duration = c.duration

        c.activeSite.replace(
            c,
            new
        )



# =========================
# remove notation
# =========================

print("remove beams")
print("remove ties")


for n in score.recurse().notes:

    n.beams = []

    if n.tie:
        n.tie = None



# =========================
# force 4/4
# =========================

print("force 4/4")


for part in score.parts:

    part.insert(
        0,
        meter.TimeSignature("4/4")
    )



# =========================
# quantize
# =========================

print("duration quantize")


for n in score.recurse().notesAndRests:

    q = float(n.duration.quarterLength)

    q = round(q * 4) / 4


    if q <= 0:
        q = 0.25


    n.duration.quarterLength = q



# =========================
# rebuild measures
# =========================

print("rebuild measures")


for part in score.parts:

    part.makeMeasures(
        inPlace=True
    )



# =========================
# split cross measure
# =========================

print("split cross measure notes")


for part in score.parts:

    try:
        part.makeNotation(
            inPlace=True
        )
    except:
        pass



# =========================
# V25 OFFSET FIX
# =========================

print("FINAL NORMALIZE OFFSET")


for part in score.parts:


    current = 0


    for n in part.recurse().notesAndRests:


        n.offset = current


        current += n.duration.quarterLength



# =========================
# remove pickup padding
# =========================

print("REMOVE PICKUP")


for part in score.parts:

    for m in part.getElementsByClass("Measure"):

        try:
            m.paddingLeft = 0
            m.paddingRight = 0
        except:
            pass



# =========================
# rebuild again
# =========================

print("rebuild measures")


for part in score.parts:

    part.makeMeasures(
        inPlace=True
    )



# =========================
# fill empty measure
# =========================

print("fill measure rest")


for part in score.parts:

    for m in part.getElementsByClass("Measure"):


        total = m.duration.quarterLength


        if total < 4:

            r = note.Rest()

            r.duration.quarterLength = 4-total

            m.append(r)



# =========================
# cache
# =========================

print("clear notation cache")

score.clearCache()



# =========================
# FINAL CHECK
# =========================

print("FINAL CHECK")


safe = True


for part in score.parts:

    for m in part.getElementsByClass("Measure"):

        length = float(
            m.duration.quarterLength
        )


        print(
            "Measure",
            m.number,
            length
        )


        if abs(length-4) > 0.01:

            safe=False



if safe:

    print("ALL MEASURES SAFE")

else:

    print("WARNING measure mismatch")



# =========================
# WRITE
# =========================

print("FINAL WRITE")


score.write(
    "musicxml",
    fp=dst
)


print("DONE")
print(dst)