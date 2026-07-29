from music21 import converter, stream, meter, note, chord
import sys
import copy


INPUT = sys.argv[1]

if len(sys.argv) >= 3:
    OUTPUT = sys.argv[2]
else:
    OUTPUT = "clean.musicxml"


print("CLEAN VERSION 20260729 v12")


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
# rebuild measures
# ==========================

print("rebuild measures v12")


new_score = stream.Score()



for part in score.parts:


    new_part = stream.Part()


    measure_no = 1

    current_measure = stream.Measure(
        number=measure_no
    )


    current_measure.insert(
        0,
        meter.TimeSignature("4/4")
    )


    used = 0.0



    for original_note in part.flatten().notesAndRests:


        duration = float(
            original_note.duration.quarterLength
        )


        while duration > 0:


            remain = 4.0 - used



            # 可以完整放入

            if duration <= remain:


                nn = copy.deepcopy(
                    original_note
                )


                nn.duration.quarterLength = duration


                current_measure.append(nn)


                used += duration


                duration = 0



            else:


                # 切割跨小節音符

                if remain > 0:


                    nn = copy.deepcopy(
                        original_note
                    )


                    nn.duration.quarterLength = remain


                    current_measure.append(nn)



                new_part.append(
                    current_measure
                )


                measure_no += 1


                current_measure = stream.Measure(
                    number=measure_no
                )


                current_measure.insert(
                    0,
                    meter.TimeSignature("4/4")
                )


                used = 0.0


                duration -= remain



    if len(current_measure.notesAndRests) > 0:

        new_part.append(
            current_measure
        )


    new_score.append(
        new_part
    )



score = new_score



# ==========================
# final check
# ==========================

print("FINAL CHECK")


note_count = 0


for part in score.parts:

    for m in part.getElementsByClass(
        stream.Measure
    ):

        total = sum(
            float(x.duration.quarterLength)
            for x in m.notesAndRests
        )


        notes = len(
            m.notes
        )


        rests = len(
            m.rests
        )


        note_count += notes


        print(
            "Measure",
            m.number,
            total,
            "notes",
            notes,
            "rests",
            rests
        )



print(
    "TOTAL NOTES",
    note_count
)



# ==========================
# write
# ==========================

print("FINAL WRITE")


score.write(
    "musicxml",
    fp=OUTPUT
)


print("DONE")
print(OUTPUT)