import sys

from music21 import (
    converter,
    stream,
    note,
    meter,
    tempo,
    duration
)


INPUT = sys.argv[1]
OUTPUT = sys.argv[2]


print("===== V17 SAFE REBUILD ENGINE =====")


# =========================
# LOAD
# =========================

print("load musicxml")

score = converter.parse(INPUT)


# =========================
# EXTRACT MELODY
# =========================

print("extract melody")

src = score.parts[0]

melody = stream.Part()

count = 0


for n in src.recurse().notes:

    if isinstance(n, note.Note):

        new_n = note.Note(n.pitch)


        ql = float(n.duration.quarterLength)


        # 移除非法 duration
        if ql <= 0:
            continue


        # 限制最大長音
        if ql > 4:
            ql = 4


        # =========================
        # QUANTIZE DURATION
        # =========================

        allowed = [
            4,
            2,
            1,
            0.5,
            0.25,
            0.125
        ]


        closest = min(
            allowed,
            key=lambda x: abs(x - ql)
        )


        new_n.duration = duration.Duration(
            closest
        )


        melody.append(new_n)

        count += 1



print(
    "notes:",
    count
)



# =========================
# FIX OCTAVE
# =========================

print("limit octave")


for n in melody.recurse().notes:

    if n.pitch.octave < 2:

        n.pitch.octave = 2


    if n.pitch.octave > 6:

        n.pitch.octave = 6



# =========================
# FORCE 4/4
# =========================

print("force 4/4")


melody.insert(
    0,
    meter.TimeSignature("4/4")
)


melody.insert(
    0,
    tempo.MetronomeMark(
        number=80
    )
)



# =========================
# REBUILD MEASURES
# =========================

print(
    "rebuild measures SAFE"
)


score2 = melody.makeMeasures(
    inPlace=False
)



# =========================
# CLEAN INVALID DURATIONS
# =========================

print(
    "final duration check"
)


for n in score2.recurse().notes:

    if n.duration.type == "inexpressible":

        print(
            "fix inexpressible:",
            n.pitch
        )

        n.duration = duration.Duration(
            0.25
        )



# =========================
# WRITE
# =========================

print(
    "WRITE"
)


score2.write(
    "musicxml",
    fp=OUTPUT
)


print(
    "DONE"
)

print(
    OUTPUT
)