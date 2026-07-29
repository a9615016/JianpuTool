from music21 import converter, stream, meter, note, chord
import sys


INPUT = sys.argv[1]

if len(sys.argv) >= 3:
    OUTPUT = sys.argv[2]
else:
    OUTPUT = "clean.musicxml"


print("CLEAN VERSION 20260729 v11")


score = converter.parse(INPUT)



# ==========================
# remove chords
# ==========================

print("remove chords")


for element in list(score.recurse()):

    if isinstance(element, chord.Chord):

        n = note.Note(
            element.pitches[0]
        )

        n.duration = element.duration

        element.activeSite.replace(
            element,
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
# duration quantize
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
        key=lambda x: abs(x-q)
    )


    n.duration.quarterLength = nearest



# ==========================
# REBUILD ALL MEASURES
# ==========================

print("rebuild measures v11")


new_score = stream.Score()



for part in score.parts:


    new_part = stream.Part()


    measure_no = 1


    m = stream.Measure(
        number=measure_no
    )


    m.insert(
        0,
        meter.TimeSignature("4/4")
    )


    used = 0.0



    for n in part.flatten().notesAndRests:


        duration = float(
            n.duration.quarterLength
        )


        while duration > 0:


            remain = 4.0 - used



            # 放得下

            if duration <= remain:


                nn = n.clone()

                nn.duration.quarterLength = duration


                m.append(nn)


                used += duration


                duration = 0



            # 放不下，需要切小節

            else:


                if remain > 0:


                    nn = n.clone()

                    nn.duration.quarterLength = remain

                    m.append(nn)



                new_part.append(m)



                measure_no += 1



                m = stream.Measure(
                    number=measure_no
                )


                m.insert(
                    0,
                    meter.TimeSignature("4/4")
                )


                used = 0.0


                duration -= remain



    # 最後一小節

    if len(m.notesAndRests) > 0:

        new_part.append(m)



    new_score.append(new_part)



score = new_score



# ==========================
# FINAL CHECK
# ==========================

print("FINAL CHECK")


for part in score.parts:

    for m in part.getElementsByClass(
        stream.Measure
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