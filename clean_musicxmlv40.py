import sys
from music21 import converter, stream, note, meter, chord, tie


print("================")
print("CLEAN MUSICXML V31")
print("FINAL JIANPU SAFE MODE")
print("================")


if len(sys.argv) < 3:
    print("usage: python clean_musicxml.py input.musicxml output.musicxml")
    sys.exit()


src = sys.argv[1]
dst = sys.argv[2]


print("read")

score = converter.parse(src)


print("flatten notes")

notes = []

for n in score.flatten().notesAndRests:

    # remove chords
    if isinstance(n, chord.Chord):
        n = n[0]

    if isinstance(n, note.Note):

        # remove tie
        n.tie = None

        dur = n.duration.quarterLength

        # hard quantize
        values = [
            4,
            2,
            1,
            0.5,
            0.25,
            0.125
        ]

        q = min(values, key=lambda x: abs(x-dur))

        n.duration.quarterLength = q

        notes.append(n)

    elif isinstance(n, note.Rest):

        dur = n.duration.quarterLength

        values = [
            4,
            2,
            1,
            0.5,
            0.25,
            0.125
        ]

        q = min(values, key=lambda x: abs(x-dur))

        n.duration.quarterLength = q

        notes.append(n)



print("rebuild score")


new_score = stream.Score()

part = stream.Part()

part.append(
    meter.TimeSignature("4/4")
)


measure = stream.Measure()
measure.number = 1

total = 0
mnum = 1


def flush_measure():

    global measure, mnum

    measure.number = mnum
    part.append(measure)

    mnum += 1

    measure = stream.Measure()



print("split measures")


for n in notes:

    dur = float(n.duration.quarterLength)


    while dur > 0:

        remain = 4-total


        if dur <= remain:

            nn = n.clone()
            nn.duration.quarterLength = dur

            measure.append(nn)

            total += dur
            dur = 0


        else:

            nn = n.clone()
            nn.duration.quarterLength = remain

            measure.append(nn)

            dur -= remain

            flush_measure()

            total = 0


        if abs(total-4) < 0.0001:

            flush_measure()
            total = 0



# fill last measure

if total > 0:

    rest = note.Rest()
    rest.duration.quarterLength = 4-total

    measure.append(rest)

    flush_measure()



new_score.insert(0, part)



print("FINAL CHECK")


safe = True


for i,m in enumerate(
    new_score.parts[0].getElementsByClass(stream.Measure),
    1
):

    length = m.duration.quarterLength

    print(
        "Measure",
        i,
        float(length)
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
    fp=dst
)


print("DONE")
print(dst)