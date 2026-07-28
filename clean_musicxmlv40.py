from music21 import converter, stream, meter, note, chord, duration
import sys
import copy


VERSION = "CLEAN MUSICXML V41 JIANPU SAFE"


print("================")
print(VERSION)
print("================")


INPUT = sys.argv[1]

if len(sys.argv) >= 3:
    OUTPUT = sys.argv[2]
else:
    OUTPUT = INPUT.replace(".musicxml", "_clean.musicxml")


print("read")

score = converter.parse(INPUT)


# =========================
# remove voices
# =========================

print("remove voices")

for p in score.parts:
    for n in p.flatten().notesAndRests:
        if hasattr(n, "voice"):
            n.voice = None



# =========================
# remove chords
# =========================

print("remove chords")

for p in score.parts:
    elements = list(p.flatten().notes)

    for c in elements:
        if isinstance(c, chord.Chord):

            highest = c.pitches[-1]

            n = note.Note(highest)

            n.duration = copy.deepcopy(c.duration)

            c.activeSite.replace(c, n)



# =========================
# remove beams
# =========================

print("remove beams")

for n in score.flatten().notes:
    try:
        n.beams = []
    except:
        pass



# =========================
# remove ties
# =========================

print("remove ties")

for n in score.flatten().notes:
    try:
        n.tie = None
    except:
        pass



# =========================
# force 4/4
# =========================

print("force 4/4")

for p in score.parts:

    p.insert(
        0,
        meter.TimeSignature("4/4")
    )



# =========================
# normalize divisions
# =========================

print("normalize divisions")

for n in score.flatten().notesAndRests:

    if n.duration.quarterLength <= 0:
        n.duration.quarterLength = 0.25



# =========================
# quantize duration
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


def quantize_length(x):

    return min(
        allowed,
        key=lambda a:abs(a-x)
    )



for n in score.flatten().notesAndRests:

    q = quantize_length(
        float(n.duration.quarterLength)
    )

    n.duration.quarterLength = q



# =========================
# rebuild measures
# =========================

print("rebuild measures")

for p in score.parts:

    p.makeMeasures(
        inPlace=True
    )



# =========================
# split crossing notes
# =========================

print("split cross measure notes")


for p in score.parts:

    measures = list(p.getElementsByClass("Measure"))


    for m in measures:

        offset = 0

        new_notes=[]


        for n in list(m.notesAndRests):

            dur = float(n.duration.quarterLength)


            if offset + dur > 4:

                remain = 4-offset


                if remain > 0:

                    first = copy.deepcopy(n)

                    first.duration.quarterLength = remain


                    second = copy.deepcopy(n)

                    second.duration.quarterLength = dur-remain


                    m.insert(
                        n.offset,
                        first
                    )

                    m.insert(
                        4,
                        second
                    )


                    n.activeSite.remove(n)

            offset += dur



# =========================
# rebuild again
# =========================

print("rebuild measures")

for p in score.parts:
    p.makeMeasures(inPlace=True)



# =========================
# fill rests
# =========================

print("fill measure rest")


for p in score.parts:

    for m in p.getElementsByClass("Measure"):

        m.padAsAnacrusis()



# =========================
# final check
# =========================

print("FINAL CHECK")


safe=True


for p in score.parts:

    for i,m in enumerate(
        p.getElementsByClass("Measure"),
        1
    ):

        length=float(
            m.duration.quarterLength
        )

        print(
            "Measure",
            i,
            length
        )

        if length > 4.01:
            safe=False



if safe:
    print("ALL MEASURES SAFE")
else:
    print("WARNING measure mismatch")



# =========================
# clear cache
# =========================

print("clear notation cache")


score.stripTies()


# =========================
# write
# =========================

print("FINAL WRITE")


score.write(
    "musicxml",
    fp=OUTPUT
)


print("DONE")
print(OUTPUT)