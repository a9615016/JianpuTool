from music21 import converter, meter, note, chord
import sys


INPUT = sys.argv[1]

if len(sys.argv) >= 3:
    OUTPUT = sys.argv[2]
else:
    OUTPUT = "clean.musicxml"


print("CLEAN VERSION 20260729 v13 PRESERVE STRUCTURE")


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
# remove chords
# ==========================

print("remove chords")


for c in list(score.recurse().getElementsByClass(chord.Chord)):

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
# quantize
# ==========================

print("duration quantize")


allowed = [
    0.25,
    0.5,
    0.75,
    1,
    1.5,
    2,
    3,
    4
]


for n in score.recurse().notesAndRests:

    q = float(
        n.duration.quarterLength
    )


    nearest = min(
        allowed,
        key=lambda x:abs(x-q)
    )


    n.duration.quarterLength = nearest



# ==========================
# force 4/4
# ==========================

print("force 4/4")


for part in score.parts:

    for m in part.getElementsByClass("Measure"):

        m.insert(
            0,
            meter.TimeSignature("4/4")
        )



# ==========================
# FIX MEASURE OVERSHOOT
# ==========================

print("fix measure overflow")


for part in score.parts:

    for m in part.getElementsByClass("Measure"):


        total = sum(
            float(x.duration.quarterLength)
            for x in m.notesAndRests
        )


        if total > 4.0:


            print(
                "TRIM",
                m.number,
                total
            )


            remain = 4.0


            remove_list=[]


            for n in list(m.notesAndRests):


                if remain <= 0:

                    remove_list.append(n)

                    continue



                d=float(
                    n.duration.quarterLength
                )



                if d <= remain:

                    remain -= d


                else:

                    n.duration.quarterLength = remain

                    remain=0



            for x in remove_list:

                m.remove(x)



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

    for m in part.getElementsByClass("Measure"):

        total=sum(
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