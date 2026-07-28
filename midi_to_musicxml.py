from music21 import converter
from music21 import stream
from music21 import note
from music21 import meter
from music21 import instrument
from music21 import duration

import sys


print("==============================")
print("MIDI TO MUSICXML V6 REBUILD MEASURE")
print("==============================")


if len(sys.argv) < 3:
    print(
        "usage: python midi_to_musicxml.py input.mid output.musicxml"
    )
    sys.exit(1)


midi_file = sys.argv[1]
output_file = sys.argv[2]


print("輸入:", midi_file)


# ==========================
# Load MIDI
# ==========================

print("讀取 MIDI")


score = converter.parse(
    midi_file
)



# ==========================
# Collect melody notes
# ==========================

print("extract melody")


raw_notes = []


for n in score.recurse().notes:

    if isinstance(n, note.Note):

        raw_notes.append(n)



print(
    "原始 notes:",
    len(raw_notes)
)



# ==========================
# Quantize
# ==========================

print("quantize")


notes = []


for n in raw_notes:


    offset = float(
        n.offset
    )


    dur = float(
        n.duration.quarterLength
    )


    # 1/16 quantize

    offset = round(
        offset * 4
    ) / 4


    dur = round(
        dur * 4
    ) / 4


    if dur < 0.25:
        dur = 0.25


    nn = note.Note(
        n.pitch
    )


    nn.duration = duration.Duration(
        dur
    )


    nn.offset = offset


    notes.append(
        nn
    )



notes.sort(
    key=lambda x:x.offset
)



# ==========================
# Rebuild clean part
# ==========================

print("REBUILD SAFE MEASURES")


part = stream.Part()


part.insert(
    0,
    instrument.Vocal()
)


part.insert(
    0,
    meter.TimeSignature("4/4")
)



# ==========================
# Split by measure
# ==========================


for n in notes:


    start = float(
        n.offset
    )


    dur = float(
        n.duration.quarterLength
    )


    remain = dur


    current = start



    while remain > 0:


        measure_start = (
            int(current // 4)
            * 4
        )


        beat_pos = (
            current - measure_start
        )


        available = 4 - beat_pos



        use = min(
            remain,
            available
        )


        nn = note.Note(
            n.pitch
        )


        nn.duration = duration.Duration(
            use
        )


        nn.offset = current



        part.insert(
            current,
            nn
        )


        current += use

        remain -= use



# ==========================
# Make measures
# ==========================

print("make measures")


part.makeMeasures(
    inPlace=True
)



print("notation")


try:

    part.makeNotation(
        inPlace=True
    )

except Exception as e:

    print(
        "notation warning:",
        e
    )



# ==========================
# Score
# ==========================

final = stream.Score()


final.insert(
    0,
    part
)



final.clearCache()



# ==========================
# Write
# ==========================

print("寫入 MusicXML")


final.write(
    "musicxml",
    fp=output_file
)


print("================")
print("完成")
print(output_file)
print("================")