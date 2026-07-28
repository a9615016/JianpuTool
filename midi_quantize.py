from music21 import converter
import sys


print("================")
print("MIDI QUANTIZE V1")
print("================")


if len(sys.argv) < 3:
    print(
        "python midi_quantize.py input.mid output.mid"
    )
    sys.exit()


inp = sys.argv[1]
out = sys.argv[2]


score = converter.parse(inp)


print("quantize notes")


# 1/16拍量化
grid = 0.25


for n in score.recurse().notes:

    offset = float(n.offset)

    new_offset = round(
        offset / grid
    ) * grid


    n.offset = new_offset



    dur = float(
        n.duration.quarterLength
    )


    new_dur = round(
        dur / grid
    ) * grid


    if new_dur <= 0:
        new_dur = grid


    n.duration.quarterLength = new_dur



print("make measures")


score.makeMeasures(
    inPlace=True
)


print("write")


score.write(
    "midi",
    fp=out
)


print("DONE")