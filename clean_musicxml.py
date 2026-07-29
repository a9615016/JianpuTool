from music21 import converter, meter, note, chord
import sys


INPUT = sys.argv[1]

if len(sys.argv) >= 3:
    OUTPUT = sys.argv[2]
else:
    OUTPUT = "clean.musicxml"


print("CLEAN VERSION 20260729 v14")


score = converter.parse(INPUT)



# ==========================
# ORIGINAL CHECK
# ==========================

print("ORIGINAL CHECK")

print(
    "NOTES",
    len(score.recurse().notes)
)

print(
    "RESTS",
    len(score.recurse().rests)
)



# ==========================
# chord -> single note
# ==========================

print("remove chords")


for c in list(
    score.recurse().getElementsByClass(chord.Chord)
):

    n = note.Note(
        c.pitches[0]
    )

    n.duration = c.duration

    c.activeSite.replace(
        c,
        n
    )



# ==========================
# remove ties
# ==========================

print("remove ties")


for n in score.recurse().notes:

    n.tie = None



# ==========================
# remove beams
# ==========================

print("remove beams")


for n in score.recurse().notes:

    try:
        n.beams = []

    except:
        pass



# ==========================
# duration normalize
# ==========================

print("duration normalize")


allowed = [
    0.25,   # 16th
    0.5,    # 8th
    0.75,
    1.0,    # quarter
    1.5,
    2.0,    # half
    3.0,
    4.0
]


for n in score.recurse().notesAndRests:


    old_type = n.duration.type

    q = float(
        n.duration.quarterLength
    )


    nearest = min(
        allowed,
        key=lambda x: abs(x-q)
    )


    if old_type in [
        "128th",
        "64th",
        "32nd"
    ]:

        print(
            "FIX SHORT NOTE",
            old_type,
            q,
            "->",
            nearest
        )


    # 清除舊 duration type
    n.duration.clear()


    # 重新設定
    n.duration.quarterLength = nearest



# ==========================
# force 4/4
# ==========================

print("force 4/4")


for part in score.parts:

    for m in part.getElementsByClass(
        "Measure"
    ):

        m.insert(
            0,
            meter.TimeSignature("4/4")
        )



# ==========================
# FINAL CHECK
# ==========================

print("FINAL CHECK")


print(
    "FINAL NOTES",
    len(score.recurse().notes)
)

print(
    "FINAL RESTS",
    len(score.recurse().rests)
)



for part in score.parts:

    for m in part.getElementsByClass(
        "Measure"
    ):

        total = sum(
            float(x.duration.quarterLength)
            for x in m.notesAndRests
        )

        print(
            "Measure",
            m.number,
            total
        )



# ==========================
# WRITE
# ==========================

print("FINAL WRITE")


score.write(
    "musicxml",
    fp=OUTPUT
)


print("DONE")
print(OUTPUT)