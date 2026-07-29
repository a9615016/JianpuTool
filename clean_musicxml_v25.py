print("CLEAN MUSICXML V25 FINAL JIANPU COMPATIBLE")

from music21 import converter, meter, note, chord, stream
import sys


print("================")
print("CLEAN MUSICXML V25 FINAL JIANPU COMPATIBLE")
print("================")


INPUT = sys.argv[1]

if len(sys.argv) >= 3:
    OUTPUT = sys.argv[2]
else:
    OUTPUT = "clean.musicxml"


# ======================
# READ
# ======================

print("read")

score = converter.parse(INPUT)


print(
    "ORIGINAL NOTES",
    len(score.recurse().notes)
)


# ======================
# REMOVE CHORDS
# ======================

print("remove chords")


for c in list(score.recurse().getElementsByClass(chord.Chord)):

    n = note.Note(c.pitches[0])

    n.duration = c.duration

    try:
        c.activeSite.replace(c, n)
    except:
        pass



# ======================
# REMOVE VOICES
# ======================

print("remove voices")


for v in score.recurse().getElementsByClass('Voice'):

    try:
        v.activeSite.remove(v)
    except:
        pass



# ======================
# REMOVE BEAMS
# ======================

print("remove beams")


for n in score.recurse().notes:

    try:
        n.beams = []
    except:
        pass



# ======================
# REMOVE TIES
# ======================

print("remove ties")


for n in score.recurse().notes:

    n.tie = None



# ======================
# QUANTIZE
# ======================

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

    q = float(n.duration.quarterLength)

    nearest = min(
        allowed,
        key=lambda x: abs(x-q)
    )

    n.duration.quarterLength = nearest



# ======================
# FORCE 4/4
# ======================

print("force 4/4")


for part in score.parts:

    part.insert(
        0,
        meter.TimeSignature("4/4")
    )



# ======================
# REBUILD MEASURES
# ======================

print("rebuild measures")


new_score = stream.Score()


for part in score.parts:


    new_part = stream.Part()

    new_part.id = part.id


    measure = stream.Measure(
        number=1
    )


    beat = 0


    for n in part.flatten().notesAndRests:


        dur = float(
            n.duration.quarterLength
        )


        # 超過4拍切割
        if beat + dur > 4:


            remain = 4 - beat


            if remain > 0:


                a = n.deepcopy()

                a.duration.quarterLength = remain

                measure.append(a)


            new_part.append(measure)


            measure = stream.Measure(
                number=len(new_part.getElementsByClass("Measure"))+1
            )


            beat = 0



            left = dur - remain


            if left > 0:


                b = n.deepcopy()

                b.duration.quarterLength = left

                measure.append(b)

                beat += left


        else:

            measure.append(
                n.deepcopy()
            )

            beat += dur



        if beat >= 4:

            new_part.append(
                measure
            )

            measure = stream.Measure(
                number=len(new_part.getElementsByClass("Measure"))+1
            )

            beat = 0



    if len(measure.notesAndRests)>0:

        while beat < 4:

            r = note.Rest()

            r.duration.quarterLength = min(
                4-beat,
                0.25
            )

            measure.append(r)

            beat += 0.25


        new_part.append(measure)



    new_score.append(new_part)



score = new_score



# ======================
# FINAL CHECK
# ======================

print("FINAL CHECK")


for part in score.parts:


    for m in part.getElementsByClass("Measure"):


        total = sum(
            float(x.duration.quarterLength)
            for x in m.notesAndRests
        )


        print(
            "Measure",
            m.number,
            total
        )


        if total > 4.001:

            print(
                "ERROR OVER 4 BEATS",
                m.number,
                total
            )



# ======================
# WRITE
# ======================

print("FINAL WRITE")


score.write(
    "musicxml",
    fp=OUTPUT
)


print("DONE")

print(OUTPUT)