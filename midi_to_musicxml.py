# ==========================================
# MIDI TO MUSICXML V2
# JIANPU COMPATIBLE
# ==========================================

import sys
from music21 import (
    converter,
    stream,
    note,
    meter,
    tempo,
    instrument
)


print("================")
print("MIDI TO MUSICXML V2")
print("================")


if len(sys.argv) < 3:
    print(
        "usage: python midi_to_musicxml.py input.mid output.musicxml"
    )
    sys.exit()


INPUT = sys.argv[1]
OUTPUT = sys.argv[2]


print("開始 MIDI → MusicXML")
print("輸入:", INPUT)


# --------------------------------
# read MIDI
# --------------------------------

print("讀取 MIDI...")

score = converter.parse(INPUT)


# --------------------------------
# rebuild melody only
# --------------------------------

print("重新整理樂譜...")


new_score = stream.Score()

part = stream.Part()

part.insert(
    0,
    instrument.Vocalist()
)


part.insert(
    0,
    meter.TimeSignature("4/4")
)


part.insert(
    0,
    tempo.MetronomeMark(
        number=80
    )
)



# --------------------------------
# collect notes
# --------------------------------

notes = []

for n in score.recurse().notes:

    if isinstance(n, note.Note):

        notes.append(n)



# sort

notes.sort(
    key=lambda x:x.offset
)



# --------------------------------
# duration quantize
# --------------------------------

allowed = [
    4,
    2,
    1,
    0.5,
    0.25
]


def quantize(x):

    return min(
        allowed,
        key=lambda a:abs(a-x)
    )



# --------------------------------
# rebuild notes
# --------------------------------


current_end = 0


for n in notes:


    new_note = note.Note(
        n.pitch
    )


    duration = float(
        n.duration.quarterLength
    )


    # quantize

    duration = quantize(
        duration
    )


    # minimum

    if duration < 0.25:
        duration = 0.25



    # remove overlap

    start = float(
        n.offset
    )


    if start < current_end:

        start = current_end



    # prevent cross measure

    measure_pos = start % 4


    if measure_pos + duration > 4:

        duration = 4 - measure_pos



    if duration <= 0:
        continue



    new_note.offset = start

    new_note.duration.quarterLength = duration


    part.insert(
        start,
        new_note
    )


    current_end = (
        start + duration
    )



# --------------------------------
# fill rests
# --------------------------------


print("補充休止符")


part.makeMeasures(
    inPlace=True
)



for m in part.getElementsByClass(
    stream.Measure
):


    total = sum(
        x.duration.quarterLength
        for x in m.notesAndRests
    )


    if total < 4:

        r = note.Rest()

        r.duration.quarterLength = (
            4-total
        )

        m.append(r)



# --------------------------------
# final clean
# --------------------------------


print("FINAL CLEAN")


for n in part.recurse().notes:

    n.tie = None

    n.beams = []



new_score.append(
    part
)



# --------------------------------
# validate
# --------------------------------


print("CHECK MEASURES")


for m in part.getElementsByClass(
    stream.Measure
):

    length=sum(
        x.duration.quarterLength
        for x in m.notesAndRests
    )

    print(
        "Measure",
        m.number,
        length
    )



# --------------------------------
# write
# --------------------------------


print("寫入 MusicXML...")


new_score.write(
    "musicxml",
    fp=OUTPUT
)


print("完成:")
print(OUTPUT)