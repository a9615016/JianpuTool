# clean_musicxml.py
# V60 BASIC-PITCH + RENDER FINAL JIANPU COMPATIBLE

import sys
from music21 import converter, meter, note, chord, stream, duration


print("================")
print("CLEAN MUSICXML V60 FINAL")
print("================")


if len(sys.argv) < 3:
    print("usage: python clean_musicxml.py input.musicxml output.musicxml")
    sys.exit(1)


input_xml = sys.argv[1]
output_xml = sys.argv[2]


print("read")

score = converter.parse(input_xml)


# -------------------------
# remove voices
# -------------------------

print("remove voices")

for part in score.parts:
    for v in part.voices:
        part.remove(v)


# -------------------------
# remove chords
# -------------------------

print("remove chords")

for part in score.parts:
    for c in list(part.recurse().getElementsByClass("Chord")):
        n = note.Note(c.root())
        n.duration = c.duration
        c.activeSite.replace(c, n)


# -------------------------
# remove beams
# -------------------------

print("remove beams")

for n in score.recurse().notes:
    n.beams = []


# -------------------------
# remove ties
# -------------------------

print("remove ties")

for n in score.recurse().notes:
    n.tie = None



# -------------------------
# force 4/4
# -------------------------

print("force 4/4")

for part in score.parts:
    part.insert(0, meter.TimeSignature("4/4"))



# -------------------------
# duration quantize
# -------------------------

print("duration quantize")


allowed = [
    4.0,
    2.0,
    1.0,
    0.5,
    0.25
]


for n in score.recurse().notesAndRests:

    q = min(
        allowed,
        key=lambda x: abs(x - n.duration.quarterLength)
    )

    n.duration = duration.Duration(q)



# -------------------------
# OFFSET QUANTIZE
# -------------------------

print("offset quantize")


for part in score.parts:

    for n in part.recurse().notesAndRests:

        new_offset = round(
            n.offset * 4
        ) / 4

        n.offset = new_offset



# -------------------------
# rebuild measures
# -------------------------

print("rebuild measures")

score.makeMeasures()



# -------------------------
# split cross measure notes
# -------------------------

print("split cross measure notes")

try:
    score.splitAtDurations()
except Exception:
    pass



# -------------------------
# second offset cleanup
# -------------------------

print("second offset quantize")


for part in score.parts:

    for n in part.recurse().notesAndRests:

        n.offset = round(
            n.offset * 4
        ) / 4



# -------------------------
# rebuild again
# -------------------------

print("rebuild measures")

score.makeMeasures()



# -------------------------
# fill empty measures
# -------------------------

print("fill measure rest")


for part in score.parts:

    for m in part.getElementsByClass("Measure"):

        length = m.duration.quarterLength

        if length < 4:

            r = note.Rest()

            r.duration = duration.Duration(
                4 - length
            )

            m.append(r)



# -------------------------
# final rebuild
# -------------------------

print("final rebuild")

score.makeMeasures()


print("clear notation cache")


# -------------------------
# FINAL CHECK
# -------------------------

print("FINAL CHECK")


safe = True


for i, m in enumerate(
    score.parts[0].getElementsByClass("Measure"),
    1
):

    q = m.duration.quarterLength

    print(
        "Measure",
        i,
        q
    )

    if abs(q-4.0) > 0.01:
        safe = False



if safe:

    print("ALL MEASURES SAFE")

else:

    print("WARNING measure mismatch")



# -------------------------
# WRITE
# -------------------------

print("FINAL WRITE")

score.write(
    "musicxml",
    fp=output_xml
)


print("DONE")
print(output_xml)