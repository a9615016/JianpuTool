import sys
import music21
from music21 import stream, note, chord, meter


print("================")
print("CLEAN MUSICXML V21")
print("================")


if len(sys.argv) < 3:
    print("usage: python clean_musicxml.py input.musicxml output.musicxml")
    sys.exit()


inp = sys.argv[1]
out = sys.argv[2]


print("input:", inp)


score = music21.converter.parse(inp)


print("remove voices")
for p in score.parts:
    p.removeByClass('Voice')


print("remove chords")
for p in score.parts:
    for c in list(p.recurse().getElementsByClass('Chord')):
        n = note.Note(c.pitches[-1])
        n.duration = c.duration
        c.activeSite.replace(c, n)


print("quantize")
score.quantizeQuarterLength(
    quarterLengthDivisors=[
        1,2,4,8,16
    ]
)


newScore = stream.Score()


for part in score.parts:

    print("rebuild measures")

    newPart = stream.Part()
    newPart.append(meter.TimeSignature("4/4"))

    currentMeasure = stream.Measure(number=1)
    currentBeat = 0


    elements = list(
        part.recurse()
        .notesAndRests
    )


    for el in elements:

        dur = el.duration.quarterLength


        # 太長音符切割
        while dur > 0:

            remain = 4 - currentBeat


            if dur <= remain:

                x = el.deepcopy()
                x.duration.quarterLength = dur

                currentMeasure.append(x)

                currentBeat += dur
                dur = 0


            else:

                x = el.deepcopy()
                x.duration.quarterLength = remain

                currentMeasure.append(x)


                dur -= remain


                currentMeasure.makeRests(fillGaps=True)


                newPart.append(currentMeasure)


                currentMeasure = stream.Measure(
                    number=currentMeasure.number + 1
                )

                currentBeat = 0


            if currentBeat == 4:

                newPart.append(currentMeasure)

                currentMeasure = stream.Measure(
                    number=currentMeasure.number + 1
                )

                currentBeat = 0


    if len(currentMeasure.notesAndRests) > 0:
        currentMeasure.makeRests(fillGaps=True)
        newPart.append(currentMeasure)


    newScore.append(newPart)


print("remove empty measures")

for p in newScore.parts:
    for m in list(p.getElementsByClass(stream.Measure)):
        if len(m.notesAndRests)==0:
            p.remove(m)


print("write")

newScore.write(
    "musicxml",
    fp=out
)


print("DONE", out)
