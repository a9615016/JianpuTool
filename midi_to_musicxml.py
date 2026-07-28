from music21 import converter
from music21 import stream
from music21 import note
from music21 import meter
from music21 import instrument
import sys


print("================")
print("MIDI TO MUSICXML V5 FINAL")
print("================")


if len(sys.argv) < 3:
    print(
        "usage: python midi_to_musicxml.py input.mid output.musicxml"
    )
    sys.exit()


src = sys.argv[1]
dst = sys.argv[2]


print("輸入:", src)


score = converter.parse(src)


print("extract melody")


part = stream.Part()

part.insert(
    0,
    instrument.Vocal()
)


notes=[]


for n in score.recurse().notes:

    if isinstance(n, note.Note):

        nn = note.Note(n.pitch)


        # 強制 16 分音符格
        offset = round(
            float(n.offset) * 4
        ) / 4


        dur = round(
            float(n.duration.quarterLength) * 4
        ) / 4


        # 最小四分之一拍
        if dur < 0.25:
            dur = 0.25


        nn.offset = offset
        nn.duration.quarterLength = dur


        notes.append(nn)



print(
    "notes:",
    len(notes)
)


notes.sort(
    key=lambda x:x.offset
)



for n in notes:

    part.insert(
        n.offset,
        n
    )



print("force 4/4")


part.insert(
    0,
    meter.TimeSignature("4/4")
)



print("make measures")


part.makeMeasures(
    inPlace=True
)



# 再一次檢查小節
print("CHECK MEASURES")


for m in part.getElementsByClass("Measure"):

    total=float(
        m.duration.quarterLength
    )

    print(
        "Measure",
        m.number,
        total
    )



score2=stream.Score()

score2.insert(
    0,
    part
)


score2.clearCache()


print("WRITE MUSICXML")


score2.write(
    "musicxml",
    fp=dst
)


print("DONE")
print(dst)