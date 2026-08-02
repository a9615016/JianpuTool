import sys
from music21 import converter, stream, note, chord, meter, tempo


INPUT = sys.argv[1]
OUTPUT = sys.argv[2]


print("MIDI CLEAN v10")


# =========================
# LOAD MIDI
# =========================

print("LOAD MIDI")

score = converter.parse(INPUT)


part = score.parts[0]


# =========================
# REMOVE CHORDS
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
# REMOVE OVERLAPS
# =========================

print("remove overlaps")


notes = list(new_part.notes)

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
# QUANTIZE
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
# FORCE 4/4
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
# MAKE MEASURES
# =========================

print("rebuild measures")


measures = new_part.makeMeasures(
    inPlace=False
)



# =========================
# FIX MEASURES
# =========================

print("fix measures")


fixed = stream.Part()


for meas in measures.getElementsByClass(
    "Measure"
):

    length = meas.duration.quarterLength


    print(
        "Measure",
        meas.number,
        length
    )


    # -----------------
    # overflow
    # -----------------

    if length > 4:

        print(
            "fix overflow",
            meas.number
        )


        # 不刪音，避免無限迴圈
        while meas.duration.quarterLength > 4:

            if len(meas.notes) == 0:
                break


            last = meas.notes[-1]


            old = last.duration.quarterLength


            last.duration.quarterLength = max(
                0.25,
                old - 0.25
            )


            # 如果沒有變化，跳出
            if (
                last.duration.quarterLength
                ==
                old
            ):
                break



    # -----------------
    # fill rest
    # -----------------

    length = meas.duration.quarterLength


    if length < 4:

        r = note.Rest()

        r.duration.quarterLength = (
            4 - length
        )

        meas.append(r)



    fixed.append(meas)



# =========================
# FINAL CHECK
# =========================

print("FINAL CHECK")


for meas in fixed.getElementsByClass(
    "Measure"
):

    print(
        "Measure",
        meas.number,
        round(
            meas.duration.quarterLength,
            3
        )
    )



# =========================
# WRITE
# =========================

print("FINAL WRITE")


fixed.write(
    "musicxml",
    fp=OUTPUT
)


print("DONE")

print(OUTPUT)