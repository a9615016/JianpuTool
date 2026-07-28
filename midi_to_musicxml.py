from music21 import converter
from music21 import stream
from music21 import note
from music21 import meter
from music21 import instrument
from music21 import duration

import sys


print("==============================")
print("MIDI TO MUSICXML V5 FINAL JIANPU")
print("==============================")


if len(sys.argv) < 3:
    print(
        "usage: python midi_to_musicxml.py input.mid output.musicxml"
    )
    sys.exit(1)


midi_file = sys.argv[1]
output_file = sys.argv[2]


print("開始 MIDI → MusicXML")
print("輸入:", midi_file)


# ==========================
# read midi
# ==========================

print("讀取 MIDI...")


score = converter.parse(
    midi_file
)



# ==========================
# 建立單旋律
# ==========================

print("extract melody...")


melody = stream.Part()


melody.insert(
    0,
    instrument.Vocal()
)



# ==========================
# collect notes
# ==========================

notes = []


for n in score.recurse().notes:

    if isinstance(n, note.Note):

        nn = note.Note(
            n.pitch
        )


        # ------------------
        # offset quantize
        # 16分音符
        # ------------------

        offset = float(
            n.offset
        )


        offset = round(
            offset * 4
        ) / 4



        # ------------------
        # duration quantize
        # ------------------

        dur = float(
            n.duration.quarterLength
        )


        dur = round(
            dur * 4
        ) / 4



        if dur <= 0:
            dur = 0.25


        if dur < 0.25:
            dur = 0.25



        nn.offset = offset


        nn.duration = duration.Duration(
            dur
        )


        notes.append(
            nn
        )



print(
    "notes:",
    len(notes)
)



# ==========================
# sort
# ==========================

notes.sort(
    key=lambda x:x.offset
)



# ==========================
# insert notes
# ==========================


for n in notes:

    melody.insert(
        n.offset,
        n
    )



# ==========================
# force 4/4
# ==========================

print("force 4/4")


melody.insert(
    0,
    meter.TimeSignature("4/4")
)



# ==========================
# rebuild measures
# ==========================

print("rebuild measures")


melody.makeMeasures(
    inPlace=True
)



# ==========================
# split crossing notes
# ==========================

print(
    "split cross measure notes"
)


try:

    melody.makeNotation(
        inPlace=True
    )

except Exception as e:

    print(
        "notation warning:",
        e
    )



# ==========================
# final score
# ==========================

final = stream.Score()


final.insert(
    0,
    melody
)



final.clearCache()



# ==========================
# write
# ==========================

print(
    "寫入 MusicXML..."
)


final.write(
    "musicxml",
    fp=output_file
)



print("================")
print("完成:")
print(output_file)
print("================")