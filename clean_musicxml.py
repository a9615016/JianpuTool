from music21 import converter, stream, note, chord, meter
import sys
import math


print("================")
print("CLEAN MUSICXML V27")
print("PUBLISH SCORE QUANTIZE + BAR REPAIR")
print("================")


input_file = sys.argv[1]
output_file = sys.argv[2]


score = converter.parse(input_file)


print("read")


# ==========================
# remove voices / chords
# ==========================

print("remove voices")
print("remove chords")


for part in score.parts:

    for element in list(part.recurse()):

        if isinstance(element, chord.Chord):

            n = note.Note(
                element.root()
            )

            n.duration = element.duration

            element.activeSite.replace(
                element,
                n
            )



# ==========================
# force 4/4
# ==========================

print("force 4/4")


for part in score.parts:

    part.insert(
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
    1,
    2,
    4
]


def quantize(q):

    return min(
        allowed,
        key=lambda x:
        abs(x-q)
    )



for n in score.recurse().notes:

    q = quantize(
        n.duration.quarterLength
    )

    n.duration.quarterLength = q



# ==========================
# rebuild measures
# ==========================

print("rebuild measures")


new_score = stream.Score()


for part in score.parts:


    new_part = stream.Part()


    current = 0


    measure_no = 1


    m = stream.Measure(
        number=measure_no
    )


    for n in part.flatten().notesAndRests:


        dur = n.duration.quarterLength


        # split cross bar
        while current + dur > 4:


            remain = 4-current


            if remain > 0:

                new_n = n.clone()

                new_n.duration.quarterLength = remain

                m.append(new_n)


            new_part.append(m)


            measure_no += 1

            m = stream.Measure(
                number=measure_no
            )


            dur -= remain

            current = 0



        n.duration.quarterLength = dur

        m.append(n)

        current += dur



        if current == 4:

            new_part.append(m)

            measure_no += 1

            m = stream.Measure(
                number=measure_no
            )

            current=0



    # fill remaining

    if current < 4:

        r = note.Rest()

        r.duration.quarterLength = 4-current

        m.append(r)


    new_part.append(m)


    new_score.append(new_part)



# ==========================
# final check
# ==========================

print("FINAL CHECK")


for m in new_score.parts[0].getElementsByClass(
    "Measure"
):

    total = sum(
        x.duration.quarterLength
        for x in m.flatten().notesAndRests
    )

    print(
        "Measure",
        m.number,
        total
    )


print("WRITE")


new_score.write(
    "musicxml",
    fp=output_file
)


print("DONE")
print(output_file)