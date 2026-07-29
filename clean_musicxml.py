from music21 import converter, stream, meter, note, chord
import sys


INPUT = sys.argv[1]

if len(sys.argv) >= 3:
    OUTPUT = sys.argv[2]
else:
    OUTPUT = "clean.musicxml"


print("CLEAN VERSION 20260729 v10")


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
# force 4/4
# ==========================
print("force 4/4")


for part in score.parts:

    for m in part.getElementsByClass(
        stream.Measure
    ):

        m.insert(
            0,
            meter.TimeSignature("4/4")
        )



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
        key=lambda x:abs(x-q)
    )


    if abs(q-nearest)>0.001:

        print(
            "FIX",
            q,
            "->",
            nearest
        )


    n.duration.quarterLength = nearest



# ==========================
# rebuild measures
# ==========================
print("rebuild measures")


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


    current = 0


    for n in part.flatten().notesAndRests:

        d = float(
            n.duration.quarterLength
        )


        # split long note

        while d > 4:

            nn = n.clone()

            nn.duration.quarterLength = 4

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


            d -= 4



        if current + d <= 4:

            nn = n.clone()

            nn.duration.quarterLength = d

            m.append(nn)

            current += d


        else:

            remain = 4-current


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


            nn = n.clone()

            nn.duration.quarterLength = d-remain

            m.append(nn)

            current = d-remain



    if len(m.notesAndRests)>0:

        new_part.append(m)


    new_score.append(new_part)



score = new_score



# ==========================
# FINAL FORCE 4/4
# ==========================
print("FINAL MEASURE FORCE 4/4")


for part in score.parts:

    for m in part.getElementsByClass(
        stream.Measure
    ):

        total = sum(
            float(n.duration.quarterLength)
            for n in m.notesAndRests
        )


        if total > 4.001:

            print(
                "TRIM MEASURE",
                m.number,
                total
            )


            remain = 4.0

            keep=[]


            for n in list(m.notesAndRests):

                if remain <= 0:
                    break


                d=float(
                    n.duration.quarterLength
                )


                if d <= remain:

                    keep.append(n)

                    remain -= d


                else:

                    nn=n.clone()

                    nn.duration.quarterLength=remain

                    keep.append(nn)

                    remain=0



            for old in list(m.notesAndRests):

                m.remove(old)


            for n in keep:

                m.append(n)



# ==========================
# FINAL CHECK
# ==========================

print("FINAL CHECK")


for part in score.parts:

    for m in part.getElementsByClass(
        stream.Measure
    ):

        total=sum(
            float(n.duration.quarterLength)
            for n in m.notesAndRests
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