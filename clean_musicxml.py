from music21 import converter, meter, stream
import sys


print("================")
print("CLEAN MUSICXML V26 PURE JIANPU")
print("================")


if len(sys.argv) < 3:
    print(
        "Usage: python clean_musicxml.py input.musicxml output.musicxml"
    )
    sys.exit(1)


src = sys.argv[1]
dst = sys.argv[2]


# =====================
# READ
# =====================

print("read")

score = converter.parse(src)



# =====================
# REMOVE COMPLEX DATA
# =====================

print("remove voices")
print("remove chords")
print("remove beams")
print("remove ties")
print("remove tuplets")


for part in score.parts:

    for n in part.recurse().notesAndRests:


        # tuplets
        try:
            n.duration.tuplets = []
        except:
            pass


        # ties
        try:
            n.tie = None
        except:
            pass


        # beams
        try:
            n.beams.fill(None)
        except:
            pass



# =====================
# FORCE 4/4
# =====================

print("force 4/4")


for part in score.parts:

    part.insert(
        0,
        meter.TimeSignature("4/4")
    )



# =====================
# QUANTIZE
# =====================

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



# =====================
# REBUILD
# =====================

print("rebuild measures")


for part in score.parts:

    part.makeMeasures(
        inPlace=True
    )



# =====================
# PURE SCORE REBUILD
# =====================

print("BUILD PURE SCORE")


pure = stream.Score()



for part in score.parts:


    new_part = stream.Part()


    for n in part.recurse().notesAndRests:


        ql = n.duration.quarterLength


        # remove invalid duration
        if ql <= 0:
            continue


        # avoid giant notes
        if ql > 4:
            ql = 4


        n.duration.quarterLength = ql


        # remove notation
        try:
            n.tie = None
        except:
            pass


        try:
            n.duration.tuplets = []
        except:
            pass


        new_part.append(n)



    # rebuild again
    new_part.makeMeasures(
        inPlace=True
    )


    pure.append(new_part)



score = pure



# =====================
# FILL EMPTY MEASURES
# =====================

print("fill measure rest")


for part in score.parts:


    for m in part.getElementsByClass(
        "Measure"
    ):


        length = m.duration.quarterLength


        if length < 4:

            m.append(
                stream.Rest(
                    quarterLength=4-length
                )
            )



# =====================
# FINAL CHECK
# =====================

print("FINAL CHECK")


safe=True


for part in score.parts:

    for i,m in enumerate(
        part.getElementsByClass("Measure"),
        1
    ):

        length=m.duration.quarterLength


        print(
            "Measure",
            i,
            length
        )


        if abs(length-4)>0.01:

            safe=False



if safe:

    print(
        "ALL MEASURES SAFE"
    )

else:

    print(
        "WARNING MEASURE ERROR"
    )



# =====================
# CACHE CLEAR
# =====================

print("clear notation cache")


score.coreElementsChanged()



# =====================
# WRITE
# =====================

print("FINAL WRITE")


score.write(
    "musicxml",
    fp=dst
)


print("DONE")
print(dst)