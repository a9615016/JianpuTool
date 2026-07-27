import sys
import music21
import os


print("================")
print("CLEAN MUSICXML V27")
print("TRUE NOTE SPLIT VERSION")
print("================")


if len(sys.argv) < 2:
    print("usage: python clean_musicxml.py input.musicxml output.musicxml")
    sys.exit(1)


input_file = sys.argv[1]

if len(sys.argv) >= 3:
    output_file = sys.argv[2]
else:
    output_file = input_file.replace(".musicxml", "_clean.musicxml")


print("read")
score = music21.converter.parse(input_file)


# ==========================
# remove voices
# ==========================

print("remove voices")

for p in score.parts:
    for el in list(p.recurse()):
        if isinstance(el, music21.note.NotRest):
            try:
                el.activeSite = None
            except:
                pass


# ==========================
# remove chords
# ==========================

print("remove chords")

for p in score.parts:
    for chord in list(p.recurse().getElementsByClass("Chord")):
        notes = chord.notes

        for n in notes:
            chord.activeSite.insert(chord.offset, n)

        chord.activeSite.remove(chord)


# ==========================
# remove notation
# ==========================

print("remove beams")
for n in score.recurse().notes:
    if hasattr(n, "beams"):
        n.beams = music21.beam.Beams()


print("remove ties")
for n in score.recurse().notes:
    n.tie = None



# ==========================
# force 4/4
# ==========================

print("force 4/4")

for p in score.parts:
    p.insert(0, music21.meter.TimeSignature("4/4"))



# ==========================
# quantize duration
# ==========================

print("duration quantize")


allowed = [
    4,
    2,
    1,
    0.5,
    0.25,
    0.125
]


def quantize(x):

    return min(
        allowed,
        key=lambda y: abs(y-x)
    )


for n in score.recurse().notes:

    q = quantize(
        float(n.duration.quarterLength)
    )

    n.duration.quarterLength = q



# ==========================
# TRUE NOTE SPLIT
# ==========================

print("TRUE NOTE SPLIT")


for part in score.parts:

    measures = part.makeMeasures()

    new_stream = music21.stream.Part()

    ts = music21.meter.TimeSignature("4/4")

    current_measure = 1
    measure_pos = 0


    for element in part.flatten().notesAndRests:

        dur = float(element.duration.quarterLength)


        while dur > 0:


            remain = 4 - measure_pos


            take = min(
                dur,
                remain
            )


            new_element = element.clone()


            new_element.duration.quarterLength = take


            new_stream.insert(
                measure_pos + (current_measure-1)*4,
                new_element
            )


            dur -= take

            measure_pos += take


            if measure_pos >= 4:

                measure_pos = 0
                current_measure += 1



    part.clear()

    for e in new_stream:
        part.insert(e.offset,e)



# ==========================
# rebuild measures
# ==========================

print("rebuild measures")

score = score.makeMeasures(
    inPlace=False
)


# ==========================
# fill rests
# ==========================

print("fill rests")


for p in score.parts:

    p.makeRests(
        fillGaps=True,
        inPlace=True
    )



# ==========================
# final check
# ==========================


print("FINAL CHECK")


for m in score.parts[0].getElementsByClass("Measure"):

    length = m.duration.quarterLength

    print(
        "Measure",
        m.number,
        length
    )


print("FINAL WRITE")


score.write(
    "musicxml",
    fp=output_file
)


print("DONE")
print(output_file)