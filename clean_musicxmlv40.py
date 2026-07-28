from music21 import converter, stream, meter, note, chord
import sys
import os


print("================")
print("CLEAN MUSICXML V25 FINAL JIANPU COMPATIBLE")
print("================")


if len(sys.argv) < 2:
    print("usage: python clean_musicxml.py input.musicxml output.musicxml")
    sys.exit()


input_file = sys.argv[1]

if len(sys.argv) >= 3:
    output_file = sys.argv[2]
else:
    output_file = "clean.musicxml"



print("read")

score = converter.parse(input_file)



# =========================
# remove extra voices
# =========================

print("remove voices")

for part in score.parts:

    for el in part.recurse():

        if isinstance(el, note.NotRest):

            if hasattr(el, "activeSite"):
                pass



# =========================
# remove chords
# =========================

print("remove chords")

for part in score.parts:

    for c in part.recurse().getElementsByClass('Chord'):

        if len(c.pitches):

            n = note.Note(c.pitches[0])
            n.duration = c.duration

            c.activeSite.replace(c, n)



# =========================
# remove beams ties
# =========================

print("remove beams")

for n in score.recurse().notes:

    n.beams = []



print("remove ties")

for n in score.recurse().notes:

    n.tie = None



# =========================
# force 4/4
# =========================

print("force 4/4")

for part in score.parts:

    part.insert(0, meter.TimeSignature("4/4"))



# =========================
# duration quantize
# =========================

print("duration quantize 1/16")


GRID = 0.25


for n in score.recurse().notesAndRests:

    old = n.duration.quarterLength

    new = round(old / GRID) * GRID


    if new <= 0:
        new = GRID


    n.duration.quarterLength = new



# =========================
# remove empty measures
# =========================

print("remove empty measures")


for part in score.parts:

    measures = list(
        part.getElementsByClass(stream.Measure)
    )

    for m in measures:

        if len(m.notesAndRests)==0:

            part.remove(m)



# =========================
# rebuild measures
# =========================

print("rebuild measures")


for part in score.parts:

    part.makeMeasures(inPlace=True)



# =========================
# split crossing notes
# =========================

print("split cross measure notes")


for part in score.parts:

    part.makeMeasures(inPlace=True)



# =========================
# fill measure rests
# =========================

print("fill measure rest")


for part in score.parts:

    for m in part.getElementsByClass(stream.Measure):

        length = m.duration.quarterLength


        if length < 4:

            r = note.Rest(
                quarterLength=4-length
            )

            m.append(r)



# =========================
# final rebuild
# =========================

print("final rebuild")


for part in score.parts:

    part.makeMeasures(inPlace=True)



# =========================
# FINAL CHECK
# =========================

print("FINAL CHECK")


bad=False


for i,m in enumerate(
    score.parts[0].getElementsByClass(stream.Measure),
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


    if abs(length-4.0)>0.01:

        bad=True



if bad:

    print("WARNING measure mismatch")

else:

    print("ALL MEASURES OK")



# =========================
# write
# =========================

print("FINAL WRITE")


score.write(
    "musicxml",
    fp=output_file
)


print("DONE")
print(output_file)