# jianpu_fix_musicxml.py
# V10 FINAL
# Brutal 4/4 rebuild for jianpu_ly compatibility

import sys
from music21 import converter, stream, note, meter, duration, clef


INPUT = sys.argv[1]
OUTPUT = sys.argv[2]


print("================")
print("JIANPU FIX MUSICXML V10 FINAL")
print("BRUTAL 4/4 REBUILD")
print("================")


score = converter.parse(INPUT)

print("read")


# -------------------------
# extract notes only
# -------------------------

notes = []

for n in score.recurse().notes:

    if isinstance(n, note.Note):

        notes.append({
            "pitch": n.pitch,
            "offset": float(n.offset),
            "quarterLength": float(n.quarterLength)
        })

    elif isinstance(n, note.Rest):

        notes.append({
            "rest": True,
            "offset": float(n.offset),
            "quarterLength": float(n.quarterLength)
        })


print("notes:", len(notes))


# sort time

notes.sort(key=lambda x:x["offset"])


# -------------------------
# create new score
# -------------------------

new_score = stream.Score()

part = stream.Part()

part.insert(0, meter.TimeSignature("4/4"))

part.insert(0, clef.TrebleClef())


BAR = 4.0


current_time = 0.0


print("rebuild timeline")


for item in notes:

    start = item["offset"]
    length = item["quarterLength"]

    if length <= 0:
        continue


    # quantize
    length = round(length * 16) / 16


    # minimum
    if length <= 0:
        length = 0.25


    pos = start


    while length > 0:


        bar_pos = pos % BAR


        remain = BAR - bar_pos


        use = min(length, remain)


        # quantize again
        use = round(use * 16) / 16


        if use <= 0:
            break


        if item.get("rest"):

            r = note.Rest()
            r.duration = duration.Duration(use)
            part.insert(pos, r)


        else:

            n = note.Note(item["pitch"])
            n.duration = duration.Duration(use)
            part.insert(pos, n)



        pos += use
        length -= use



# -------------------------
# rebuild measures
# -------------------------

print("make measures")

part.makeMeasures(inPlace=True)


# -------------------------
# force 4/4
# -------------------------

for m in part.getElementsByClass("Measure"):

    m.timeSignature = meter.TimeSignature("4/4")


# -------------------------
# fill empty beat
# -------------------------

print("final check")


for i,m in enumerate(part.getElementsByClass("Measure"),1):

    q = m.duration.quarterLength

    print("Measure",i,q)

    if q < 4:

        rest = note.Rest()
        rest.duration = duration.Duration(4-q)
        m.append(rest)


# rebuild

part.makeMeasures(inPlace=True)


new_score.insert(0,part)


print("write")

new_score.write(
    "musicxml",
    fp=OUTPUT
)


print("DONE")
print(OUTPUT)