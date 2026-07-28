print("================")
print("CLEAN MUSICXML V36 FORCE SPLIT NOTE")
print("================")

from music21 import converter, stream, note, chord, meter
import sys


def force_split_measure_notes(score):

    print("force split cross measure notes")

    for part in score.parts:

        new_part = stream.Part()

        for m in part.getElementsByClass('Measure'):

            new_measure = stream.Measure(number=m.number)

            used = 0.0
            target = 4.0

            for n in m.notesAndRests:

                dur = float(n.duration.quarterLength)

                # 超過小節剩餘容量
                while used + dur > target:

                    remain = target - used

                    if remain > 0:
                        nn = n.clone()
                        nn.duration.quarterLength = remain
                        new_measure.append(nn)

                    dur -= remain
                    used = 0

                    # 剩餘建立下一小節
                    new_measure = stream.Measure(number=m.number)

                if dur > 0:
                    nn = n.clone()
                    nn.duration.quarterLength = dur
                    new_measure.append(nn)

                used += dur

            new_part.append(new_measure)

        part.removeByClass('Measure')
        part.append(new_part.getElementsByClass('Measure'))

    return score



input_file=sys.argv[1]
output_file=sys.argv[2]


score=converter.parse(input_file)

print("read")

# 移除問題元素
print("remove voices")
for p in score.parts:
    for n in p.recurse():
        if hasattr(n,"voice"):
            n.voice=None


print("remove chords")
for p in score.parts:
    for c in list(p.recurse().getElementsByClass('Chord')):
        c_notes=c.notes
        for n in c_notes:
            c.activeSite.insert(c.offset,n)
        c.activeSite.remove(c)


print("remove beams")
for n in score.recurse().notes:
    n.beams.clear()


print("remove ties")
for n in score.recurse().notes:
    n.tie=None


print("force 4/4")

for p in score.parts:
    p.insert(0,meter.TimeSignature('4/4'))


print("duration quantize")

for n in score.recurse().notesAndRests:
    q=n.duration.quarterLength

    if q < 0.25:
        n.duration.quarterLength=0.25
    elif q < 0.5:
        n.duration.quarterLength=0.5
    elif q < 1:
        n.duration.quarterLength=1


print("rebuild measures")

for p in score.parts:
    p.makeMeasures(inPlace=True)



# V36核心
score=force_split_measure_notes(score)


print("fill measure rest")

for p in score.parts:
    for m in p.getElementsByClass('Measure'):

        total=sum(
            x.duration.quarterLength
            for x in m.notesAndRests
        )

        if total < 4:
            r=note.Rest()
            r.duration.quarterLength=4-total
            m.append(r)



print("FINAL CHECK")

ok=True

for p in score.parts:
    for m in p.getElementsByClass('Measure'):

        total=sum(
            x.duration.quarterLength
            for x in m.notesAndRests
        )

        print("Measure",m.number,total)

        if abs(total-4)>0.01:
            ok=False


if ok:
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