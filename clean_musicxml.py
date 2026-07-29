from music21 import converter, stream, note, chord, meter, tempo
import sys


INPUT = sys.argv[1]
OUTPUT = sys.argv[2]


print("================")
print("CLEAN MUSICXML V25")
print("JIANPU STRICT 4/4")
print("================")


# ======================
# Load
# ======================

print("read")

score = converter.parse(INPUT)


part = score.parts[0]


# ======================
# Remove voices
# ======================

print("remove voices")


flat = part.flatten()


new_part = stream.Part()



# ======================
# Remove chords
# ======================

print("remove chords")


for n in flat.notesAndRests:


    if isinstance(n, chord.Chord):

        x = note.Note(
            n.pitches[-1]
        )

        x.offset = n.offset
        x.duration = n.duration

        new_part.append(x)


    else:

        new_part.append(n)



# ======================
# Remove ties
# ======================

print("remove ties")


for n in new_part.notes:

    n.tie = None



# ======================
# Remove beams
# ======================

print("remove beams")



# ======================
# Quantize timing
# ======================

print("duration quantize")


GRID = [
    4,
    2,
    1,
    0.5,
    0.25
]


def quantize(value):

    return min(
        GRID,
        key=lambda x:
        abs(x-value)
    )



for n in new_part.notes:


    d = float(
        n.duration.quarterLength
    )


    n.duration.quarterLength = quantize(d)



# ======================
# force 4/4
# ======================

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



# ======================
# Make measures
# ======================

print("rebuild measures")


measures = new_part.makeMeasures()



# ======================
# Fix measure length
# ======================

print("fix measure")


fixed = stream.Part()


for m in measures.getElementsByClass(
    "Measure"
):


    length = float(
        m.duration.quarterLength
    )


    print(
        "Before",
        m.number,
        length
    )


    # 太長
    if length > 4:


        remain = 4


        rebuilt = []


        for n in m.notesAndRests:


            if remain <= 0:
                break


            d = min(
                float(n.duration.quarterLength),
                remain
            )


            n.duration.quarterLength = d

            rebuilt.append(n)

            remain -= d



        m = stream.Measure(
            number=m.number
        )


        for n in rebuilt:

            m.append(n)



        length = m.duration.quarterLength



    # 太短補 rest

    if length < 4:


        r = note.Rest()

        r.duration.quarterLength = (
            4-length
        )

        m.append(r)



    fixed.append(m)



# ======================
# FINAL CHECK
# ======================

print("clear notation cache")


fixed.coreElementsChanged()


print("FINAL CHECK")


ok=True


for m in fixed.getElementsByClass(
    "Measure"
):


    length=round(
        float(
            m.duration.quarterLength
        ),
        3
    )


    print(
        "Measure",
        m.number,
        length
    )


    if length != 4:

        ok=False



if ok:

    print("PASS 4/4")

else:

    print("WARNING mismatch")



# ======================
# Write
# ======================

print("FINAL WRITE")


fixed.write(
    "musicxml",
    fp=OUTPUT
)


print("DONE")
print(OUTPUT)