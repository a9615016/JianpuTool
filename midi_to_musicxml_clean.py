import sys
import os
from music21 import converter, stream, note, chord, meter, tempo


INPUT = sys.argv[1]
OUTPUT = sys.argv[2]


print("MIDI CLEAN v9")


# =========================
# MIDI LOAD
# =========================

print("LOAD MIDI")

score = converter.parse(INPUT)


# =========================
# get melody part
# =========================

part = score.parts[0]


# =========================
# remove chords
# =========================

print("remove chords")

new_part = stream.Part()


for el in part.flatten().notesAndRests:

    if isinstance(el, chord.Chord):

        n = note.Note(
            el.pitches[-1]
        )

        n.duration = el.duration

        new_part.append(n)


    else:

        new_part.append(el)



# =========================
# remove overlaps
# =========================

print("remove overlaps")


notes = list(
    new_part.notes
)


notes.sort(
    key=lambda x:x.offset
)


last_end = 0


for n in notes:

    if n.offset < last_end:

        n.offset = last_end


    last_end = (
        n.offset +
        n.duration.quarterLength
    )



# =========================
# duration quantize
# =========================

print("duration quantize")


allowed = [
    4,
    2,
    1,
    0.5,
    0.25,
    0.125
]


for n in new_part.notes:

    d = float(
        n.duration.quarterLength
    )


    closest = min(
        allowed,
        key=lambda x:abs(x-d)
    )


    n.duration.quarterLength = closest



# =========================
# force 4/4
# =========================

print("force 4/4")


new_part.insert(
    0,
    meter.TimeSignature("4/4")
)


new_part.insert(
    0,
    tempo.MetronomeMark(
        number=80
    )
)



# =========================
# rebuild measures
# =========================

print("rebuild measures")


m = new_part.makeMeasures(
    inPlace=False
)



# =========================
# split cross measure notes
# =========================

print(
    "split cross measure notes"
)


m = m.expandRepeats()


# =========================
# pad / fix measures
# =========================

fixed = stream.Part()


for meas in m.getElementsByClass(
    "Measure"
):

    length = (
        meas.duration.quarterLength
    )


    print(
        "Measure",
        meas.number,
        length
    )


    # 超過4拍
    if length > 4:

        print(
            "fix overflow",
            meas.number
        )


        while (
            meas.duration.quarterLength > 4
        ):

            last = meas.notes[-1]

            last.duration.quarterLength = (
                max(
                    0.25,
                    last.duration.quarterLength-0.25
                )
            )


    # 不足補rest

    length = (
        meas.duration.quarterLength
    )


    if length < 4:

        r = note.Rest()

        r.duration.quarterLength = (
            4-length
        )

        meas.append(r)



    fixed.append(meas)



# =========================
# FINAL CHECK
# =========================

print("FINAL CHECK")


ok = True


for meas in fixed.getElementsByClass(
    "Measure"
):

    l = round(
        meas.duration.quarterLength,
        3
    )

    print(
        "Measure",
        meas.number,
        l
    )


    if l != 4:

        ok=False



if not ok:

    print(
        "WARNING measure mismatch"
    )


else:

    print(
        "PASS"
    )



# =========================
# WRITE
# =========================

print(
    "FINAL WRITE"
)


fixed.write(
    "musicxml",
    fp=OUTPUT
)


print(
    "DONE"
)

print(
    OUTPUT
)