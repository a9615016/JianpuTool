# CLEAN MUSICXML V31
# FINAL JIANPU COMPATIBLE
# FORCE 4/4 SPLIT MEASURES

from music21 import converter, stream, note, chord, meter
import sys


print("================")
print("CLEAN MUSICXML V31 FORCE SPLIT")
print("================")


src = sys.argv[1]
dst = sys.argv[2]


print("read")

score = converter.parse(src)


# ----------------------------
# remove voices
# ----------------------------
print("remove voices")

for p in score.parts:
    for n in p.recurse():
        if hasattr(n, "voice"):
            n.voice = None


# ----------------------------
# remove chords
# ----------------------------
print("remove chords")

for p in score.parts:
    for c in list(p.recurse().getElementsByClass("Chord")):
        new = note.Note(c.root())
        new.duration = c.duration
        c.activeSite.replace(c, new)


# ----------------------------
# remove notation
# ----------------------------
print("remove beams")
print("remove ties")

for n in score.recurse().notes:
    if hasattr(n, "tie"):
        n.tie = None


# ----------------------------
# force 4/4
# ----------------------------
print("force 4/4")

for p in score.parts:
    p.insert(0, meter.TimeSignature("4/4"))


# ----------------------------
# quantize
# ----------------------------
print("duration quantize")

for n in score.recurse().notesAndRests:

    q = n.duration.quarterLength

    # round to 1/12 beat
    q = round(float(q) * 12) / 12

    if q <= 0:
        q = 1/12

    n.duration.quarterLength = q



# ----------------------------
# rebuild measures
# ----------------------------
print("rebuild measures")


new_score = stream.Score()


for part in score.parts:

    new_part = stream.Part()
    new_part.insert(0, meter.TimeSignature("4/4"))

    current = 0

    for element in part.flatten().notesAndRests:

        dur = float(element.duration.quarterLength)


        # split over measure
        while current + dur > 4.0:

            remain = 4.0 - current


            if remain > 0:

                temp = element.clone()
                temp.duration.quarterLength = remain
                new_part.append(temp)


            dur -= remain
            current = 0


            print("split measure")


        temp = element.clone()
        temp.duration.quarterLength = dur

        new_part.append(temp)

        current += dur


        if abs(current - 4.0) < 0.001:
            current = 0


    # fill last measure

    if current > 0:

        rest = note.Rest()
        rest.duration.quarterLength = 4-current
        new_part.append(rest)


    new_score.append(new_part)



score = new_score



# ----------------------------
# make measures
# ----------------------------
print("make measures")

for p in score.parts:

    p.makeMeasures(inPlace=True)



# ----------------------------
# final check
# ----------------------------

print("FINAL CHECK")


safe = True

for i,m in enumerate(score.parts[0].getElementsByClass("Measure")):

    length = float(m.duration.quarterLength)

    print(
        "Measure",
        i+1,
        length
    )

    if abs(length-4.0)>0.001:
        safe=False



if safe:
    print("ALL MEASURES SAFE")
else:
    print("WARNING measure mismatch")



print("FINAL WRITE")

score.write(
    "musicxml",
    fp=dst
)


print("DONE")
print(dst)