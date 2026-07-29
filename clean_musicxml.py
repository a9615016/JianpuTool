from music21 import converter, stream, meter, note, chord, tie
import sys


INPUT = sys.argv[1]

if len(sys.argv) >= 3:
    OUTPUT = sys.argv[2]
else:
    OUTPUT = "clean.musicxml"


print("CLEAN VERSION 20260729 v9")


score = converter.parse(INPUT)


# ==========================
# remove chords
# ==========================
print("remove chords")

for part in score.parts:
    for element in list(part.recurse()):
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

    if n.tie:
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
        key=lambda x: abs(x-q)
    )

    if abs(q-nearest) > 0.001:

        print(
            "quantize",
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

    meter_obj = meter.TimeSignature("4/4")

    new_part.append(meter_obj)

    measure_no = 1
    current = stream.Measure(
        number=measure_no
    )

    current.insert(
        0,
        meter.TimeSignature("4/4")
    )


    total = 0


    for n in part.flatten().notesAndRests:

        length = float(
            n.duration.quarterLength
        )


        # 超長音拆分
        while length > 4:

            nn = n.clone()

            nn.duration.quarterLength = 4

            current.append(nn)

            length -= 4

            if current.duration.quarterLength >= 4:

                new_part.append(current)

                measure_no += 1

                current = stream.Measure(
                    number=measure_no
                )

                current.insert(
                    0,
                    meter.TimeSignature("4/4")
                )


        if length > 0:

            nn = n.clone()

            nn.duration.quarterLength = length

            if current.duration.quarterLength + length <= 4:

                current.append(nn)

            else:

                remain = (
                    4 -
                    current.duration.quarterLength
                )

                if remain > 0:

                    part1 = nn.clone()

                    part1.duration.quarterLength = remain

                    current.append(part1)


                new_part.append(current)

                measure_no += 1

                current = stream.Measure(
                    number=measure_no
                )

                current.insert(
                    0,
                    meter.TimeSignature("4/4")
                )


                part2 = nn.clone()

                part2.duration.quarterLength = (
                    length-remain
                )

                current.append(part2)



    if len(current.notesAndRests) > 0:

        new_part.append(current)


    new_score.append(new_part)



score = new_score



# ==========================
# FINAL duration normalize
# ==========================
print("FINAL DURATION FIX")


for part in score.parts:

    for m in part.getElementsByClass(
        stream.Measure
    ):

        total = sum(
            float(x.duration.quarterLength)
            for x in m.notesAndRests
        )


        if abs(total-4) > 0.01:

            print(
                "WARNING measure mismatch",
                m.number,
                total
            )



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