import sys
from music21 import converter, stream, meter, note, chord
from fractions import Fraction


if len(sys.argv) < 3:
    print("usage: final_quantize.py input.musicxml output.musicxml")
    sys.exit(1)


input_file = sys.argv[1]
output_file = sys.argv[2]


print("Loading:", input_file)


score = converter.parse(input_file)


# ===============================
# 強制建立 4/4 小節
# ===============================

score = score.makeMeasures(
    inPlace=False
)


for part in score.parts:

    part.insert(
        0,
        meter.TimeSignature("4/4")
    )


# ===============================
# 量化音符
# ===============================

for part in score.parts:

    for n in part.recurse():

        if isinstance(n, note.Note):

            q = Fraction(
                n.quarterLength
            ).limit_denominator(16)

            n.quarterLength = float(q)


        elif isinstance(n, chord.Chord):

            q = Fraction(
                n.quarterLength
            ).limit_denominator(16)

            n.quarterLength = float(q)



# ===============================
# 再次建立 Measures
# ===============================

new_score = stream.Score()


for part in score.parts:

    new_part = stream.Part()

    for m in part.getElementsByClass("Measure"):

        new_part.append(m)


    new_score.append(new_part)



# 如果沒有 measure，補救

if len(new_score.parts[0].getElementsByClass("Measure")) == 0:

    print("沒有Measures，重新切割")

    new_score = score.makeMeasures(
        inPlace=False
    )



print("Writing:", output_file)


new_score.write(
    "musicxml",
    fp=output_file
)


print("FINAL QUANTIZE OK")