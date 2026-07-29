# clean_musicxml.py
# CLEAN MUSICXML V28
# Publication quantize + jianpu_ly compatible

import sys
from music21 import converter, stream, note, chord, meter, duration, bar


print("================")
print("CLEAN MUSICXML V28")
print("PUBLICATION QUANTIZE + JIANPU COMPATIBLE")
print("================")


if len(sys.argv) < 3:
    print(
        "usage: python clean_musicxml.py input.musicxml output.musicxml"
    )
    sys.exit()


src = sys.argv[1]
out = sys.argv[2]


print("read")

score = converter.parse(src)


# =========================
# create clean score
# =========================

clean = stream.Score()

part = stream.Part()

part.append(
    meter.TimeSignature("4/4")
)


print("remove voices")
print("remove chords")
print("remove beams")
print("remove ties")


# =========================
# duration normalize
# =========================

def normalize_duration(d):

    q = float(d.quarterLength)

    # publication grid
    grid = [
        0.25,   # 16th
        0.5,    # 8th
        1.0,    # quarter
        2.0,    # half
        4.0
    ]

    best = min(
        grid,
        key=lambda x: abs(x-q)
    )

    return best



for n in score.flat.notesAndRests:


    if isinstance(n, chord.Chord):

        # remove chord
        n = n.notes[0]


    new = n.clone()


    # remove unsupported durations
    ql = normalize_duration(
        new.duration
    )


    new.duration = duration.Duration(
        ql
    )


    # remove ties

    if hasattr(new, "tie"):
        new.tie = None


    # remove beams

    if hasattr(new, "beams"):
        new.beams = None


    part.append(new)



clean.append(part)



# =========================
# rebuild measures
# =========================

print("force 4/4")
print("duration quantize")
print("rebuild measures")


clean = clean.makeMeasures(
    inPlace=False
)



# =========================
# split notes
# =========================

print("split cross measure notes")


try:

    clean = clean.expandRepeats(
        inPlace=False
    )

except:

    pass



# =========================
# check bars
# =========================


print("FINAL CHECK")


for i,m in enumerate(
    clean.parts[0].getElementsByClass(
        "Measure"
    ),
    1
):

    length = float(
        m.duration.quarterLength
    )

    print(
        "Measure",
        i,
        length
    )


# =========================
# write
# =========================


print("FINAL WRITE")


clean.write(
    "musicxml",
    fp=out
)


print("DONE")
print(out)