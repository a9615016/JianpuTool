from music21 import converter, meter, stream
import sys


print("================")
print("CLEAN MUSICXML V26 JIANPU SAFE")
print("================")


if len(sys.argv) < 3:
    print(
        "Usage: python clean_musicxml.py input.musicxml output.musicxml"
    )
    sys.exit(1)


src = sys.argv[1]
dst = sys.argv[2]


print("read")

score = converter.parse(src)



# =========================
# Remove voices / chords
# =========================

print("remove voices")
print("remove chords")


for part in score.parts:

    for n in list(part.recurse()):

        if hasattr(n, "voices"):

            try:
                n.voices = []
            except:
                pass


        if n.__class__.__name__ == "Chord":

            try:
                n.removeRedundantPitchClasses()
            except:
                pass



# =========================
# Remove notation
# =========================

print("remove beams")
print("remove ties")


for n in score.recurse().notes:


    try:
        n.beams.fill(None)
    except:
        pass


    try:
        n.tie = None
    except:
        pass


    try:
        n.duration.tuplets = []
    except:
        pass



# =========================
# Force 4/4
# =========================

print("force 4/4")


for part in score.parts:

    part.insert(
        0,
        meter.TimeSignature("4/4")
    )



# =========================
# Quantize duration
# =========================

print("duration quantize")


score.quantize(
    quarterLengthDivisors=[
        1,
        2,
        4,
        8,
        16
    ]
)



# =========================
# Split notes crossing bar
# =========================

print("split cross measure notes")


for part in score.parts:

    try:

        part.makeMeasures(
            inPlace=True
        )

    except Exception as e:

        print(e)



# =========================
# FINAL STRICT REBUILD
# =========================


print("FINAL REBUILD MEASURES")


for part in score.parts:


    measures = part.makeMeasures(
        inPlace=False
    )


    for m in measures:

        total = 0


        for n in m.notesAndRests:

            total += n.duration.quarterLength


        # 補休止
        if total < 4:

            m.append(
                stream.Rest(
                    quarterLength=4-total
                )
            )


    part.remove(
        part.measures
    )


    for m in measures:

        part.append(m)



# =========================
# Final Check
# =========================


print("FINAL CHECK")


ok=True


for i,m in enumerate(
    score.parts[0].getElementsByClass("Measure"),
    1
):

    length=m.duration.quarterLength

    print(
        "Measure",
        i,
        length
    )


    if abs(length-4)>0.01:

        ok=False



if ok:

    print(
        "ALL MEASURES SAFE"
    )

else:

    print(
        "WARNING measure mismatch"
    )



# =========================
# Clear cache
# =========================

print("clear notation cache")


score.coreElementsChanged()



# =========================
# Write
# =========================

print("FINAL WRITE")


score.write(
    "musicxml",
    fp=dst
)


print(
    "DONE"
)

print(dst)