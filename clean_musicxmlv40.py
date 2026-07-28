from music21 import converter, stream, note, chord, meter
import sys


print("================")
print("CLEAN MUSICXML V43 JIANPU SAFE")
print("================")


input_file = sys.argv[1]
output_file = sys.argv[2]


print("read")
score = converter.parse(input_file)


print("remove voices")
for p in score.parts:
    for n in p.recurse():
        if hasattr(n, "voice"):
            n.voice = None


print("remove chords")
for p in score.parts:
    for c in list(p.recurse().getElementsByClass("Chord")):
        n = note.Note(c.pitches[0])
        n.duration = c.duration
        c.activeSite.replace(c, n)



print("remove beams ties tuplets")

for n in score.recurse():

    if isinstance(n, note.Note):

        n.tie = None

        try:
            n.duration.tuplets = []
        except:
            pass

        if n.beams:
            n.beams = []


print("force 4/4")

for p in score.parts:
    p.insert(0, meter.TimeSignature("4/4"))



print("QUANTIZE")


allowed = [
    4.0,
    2.0,
    1.0,
    0.5,
    0.25
]


def quantize_duration(q):

    best = min(
        allowed,
        key=lambda x: abs(x-q)
    )

    return best



for n in score.recurse():

    if isinstance(n, note.Note):

        q = float(n.duration.quarterLength)

        newq = quantize_duration(q)

        n.duration.quarterLength = newq



print("rebuild measures")


for p in score.parts:

    measures = p.makeMeasures(inPlace=False)

    p.remove(*p.getElementsByClass("Measure"))

    for m in measures.getElementsByClass("Measure"):
        p.append(m)



print("fill measure rest")


for p in score.parts:

    for m in p.getElementsByClass("Measure"):

        length = float(m.duration.quarterLength)

        if length < 4:

            r = note.Rest()

            r.duration.quarterLength = 4-length

            m.append(r)



print("FINAL CHECK")


safe = True

for p in score.parts:

    for i,m in enumerate(
        p.getElementsByClass("Measure"),
        1
    ):

        length=float(m.duration.quarterLength)

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

score.write(
    "musicxml",
    fp=output_file
)


print("DONE")
print(output_file)