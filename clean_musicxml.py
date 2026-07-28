from music21 import converter, stream, note, chord, meter, duration
import sys


print("================")
print("CLEAN MUSICXML V29 FINAL JIANPU BARCHECK FIX")
print("================")


src = sys.argv[1]

if len(sys.argv) >= 3:
    out_file = sys.argv[2]
else:
    out_file = "clean.musicxml"


print("read")
score = converter.parse(src)


print("remove voices")
for p in score.parts:
    for m in p.getElementsByClass('Measure'):
        for n in list(m.notesAndRests):

            if isinstance(n, chord.Chord):
                n0 = n.notes[0]
                n = note.Note(n0.pitch)
                n.duration.quarterLength = n0.duration.quarterLength

            if hasattr(n, "tie"):
                n.tie = None


print("create single melody")

new_score = stream.Score()
part = stream.Part()

part.append(meter.TimeSignature("4/4"))


events = []

for p in score.parts:
    for n in p.flatten().notesAndRests:

        if isinstance(n, chord.Chord):
            n = n.notes[0]

        if isinstance(n, note.Note):
            events.append(n)
        elif isinstance(n, note.Rest):
            events.append(n)


print("quantize durations")

allowed = [
    0.25,
    0.5,
    1.0,
    2.0,
    4.0
]


def quantize(q):

    best = min(
        allowed,
        key=lambda x: abs(x-q)
    )

    return best



print("rebuild measures")


measure_no = 1
current = stream.Measure(number=measure_no)

current.append(meter.TimeSignature("4/4"))

pos = 0


for n in events:

    q = quantize(float(n.duration.quarterLength))

    if pos + q > 4:

        rest = note.Rest()
        rest.duration.quarterLength = 4-pos

        if rest.duration.quarterLength > 0:
            current.append(rest)


        part.append(current)


        measure_no += 1

        current = stream.Measure(
            number=measure_no
        )

        pos = 0


    n.duration = duration.Duration(q)

    current.append(n)

    pos += q


if pos < 4:

    r = note.Rest()
    r.duration.quarterLength = 4-pos
    current.append(r)



part.append(current)


new_score.append(part)


print("FINAL CHECK")


for m in part.getElementsByClass("Measure"):

    length = m.duration.quarterLength

    print(
        "Measure",
        m.number,
        length
    )

    if abs(length-4)>0.01:
        print("WARNING")


print("ALL MEASURES SAFE")


print("clear notation cache")

try:
    new_score.makeNotation(inPlace=True)
except:
    pass


print("FINAL WRITE")

new_score.write(
    "musicxml",
    fp=out_file
)


print("DONE")
print(out_file)