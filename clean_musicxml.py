import sys
import music21
import os


print("================")
print("CLEAN MUSICXML V19")
print("================")


if len(sys.argv) < 3:
    print("usage: python clean_musicxml.py input.musicxml output.musicxml")
    sys.exit(1)


input_file = sys.argv[1]
output_file = sys.argv[2]


print("input:", input_file)


score = music21.converter.parse(input_file)


# -------------------------
# 移除複雜結構
# -------------------------

print("remove voices")
for p in score.parts:
    for m in p.getElementsByClass('Measure'):
        for v in m.voices:
            m.remove(v)


print("remove chords")

for p in score.parts:
    for chord in list(p.recurse().getElementsByClass('Chord')):
        notes = chord.notes
        for n in notes:
            chord.activeSite.insert(chord.offset, n)
        chord.activeSite.remove(chord)


# -------------------------
# 單聲部
# -------------------------

for p in score.parts:

    notes = []

    for n in p.recurse().notesAndRests:
        notes.append(n)

    p.removeByClass('Measure')

    measure = music21.stream.Measure()
    offset = 0


    print("rebuild measures")


    for n in notes:

        ql = n.duration.quarterLength


        # 防止超長
        if ql > 4:
            print("trim long note:", ql)
            n.duration.quarterLength = 4


        # 超過小節
        if offset + n.duration.quarterLength > 4:

            remain = 4 - offset

            if remain > 0:

                print(
                    "split overflow:",
                    offset,
                    "+",
                    n.duration.quarterLength
                )

                first = n.deepcopy()
                first.duration.quarterLength = remain
                measure.append(first)

            p.append(measure)

            measure = music21.stream.Measure()
            offset = 0


            # 剩餘部分
            left = n.duration.quarterLength - remain

            if left > 0:
                second = n.deepcopy()
                second.duration.quarterLength = left
                measure.append(second)
                offset = left

        else:

            measure.append(n)
            offset += n.duration.quarterLength


        if offset >= 4:

            p.append(measure)
            measure = music21.stream.Measure()
            offset = 0


    if len(measure.notesAndRests) > 0:
        p.append(measure)



# -------------------------
# 4/4
# -------------------------

print("force 4/4")

for p in score.parts:

    for m in p.getElementsByClass('Measure'):

        m.timeSignature = music21.meter.TimeSignature('4/4')


# -------------------------
# quantize
# -------------------------

print("quantize")

score.quantize(
    quarterLengthDivisors=[
        4,8,16
    ]
)



# -------------------------
# 移除空小節
# -------------------------

print("remove empty measures")

for p in score.parts:

    for m in list(p.getElementsByClass('Measure')):

        if len(m.notesAndRests)==0:
            p.remove(m)



print("write")

score.write(
    "musicxml",
    fp=output_file
)


print("DONE", output_file)
