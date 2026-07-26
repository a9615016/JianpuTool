import sys
import music21
from music21 import note, chord, stream


print("CLEAN VERSION 20260726 V14")
print("Force split crossing notes")


input_file = sys.argv[1]

if len(sys.argv) >= 3:
    output_file = sys.argv[2]
else:
    output_file = input_file.replace(
        ".musicxml",
        "_clean.musicxml"
    )


score = music21.converter.parse(input_file)


# =========================
# remove voices
# =========================

for p in score.parts:

    for v in p.voices:
        v.remove(v[:])



# =========================
# remove chords
# =========================

for p in score.parts:

    for c in p.recurse().getElementsByClass(
        chord.Chord
    ):

        n = note.Note(
            c.pitches[0]
        )

        n.duration = c.duration

        c.activeSite.replace(
            c,
            n
        )



# =========================
# remove grace
# =========================

for g in score.recurse().notes:

    if g.duration.isGrace:

        g.activeSite.remove(g)



# =========================
# FORCE 4/4
# =========================

for p in score.parts:

    measures = p.getElementsByClass(
        stream.Measure
    )

    for m in measures:

        ts = m.timeSignature

        if ts is None:

            m.insert(
                0,
                music21.meter.TimeSignature("4/4")
            )



# =========================
# SPLIT CROSS BAR NOTES
# =========================

for p in score.parts:

    new_part = stream.Part()

    current_measure = 1
    used = 0

    measure_length = 4.0


    for n in p.recurse().notesAndRests:


        dur = n.duration.quarterLength


        while dur > 0:


            remain = (
                measure_length
                -
                used
            )


            if dur <= remain:


                n2 = n.clone()

                n2.duration.quarterLength = dur

                new_part.append(n2)


                used += dur
                dur = 0



            else:

                # split first part

                n1 = n.clone()

                n1.duration.quarterLength = remain


                if isinstance(
                    n1,
                    note.Note
                ):

                    n1.tie = music21.tie.Tie(
                        "start"
                    )


                new_part.append(n1)


                dur -= remain


                # next measure

                current_measure += 1

                used = 0


                n3 = n.clone()

                n3.duration.quarterLength = dur


                if isinstance(
                    n3,
                    note.Note
                ):

                    n3.tie = music21.tie.Tie(
                        "stop"
                    )


                new_part.append(n3)

                used = dur
                dur = 0



        if used >= measure_length:

            current_measure += 1
            used = 0



    p.clear()

    for e in new_part:

        p.append(e)



# =========================
# quantize
# =========================

score.quantize(
    quarterLengthDivisors=[
        4,
        8,
        16
    ]
)



score.write(
    "musicxml",
    fp=output_file
)


print("DONE:")
print(output_file)