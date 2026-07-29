print("######## CLEAN MUSICXML V34 ACTIVE ########")
# ==========================================================
# CLEAN MUSICXML V34
# jianpu_ly compatible
# force 4/4 + quantize + bar repair
# ==========================================================

import sys
from music21 import converter, stream, meter, note, chord, duration


print("==============================")
print("CLEAN MUSICXML V34")
print("force 4/4 + quantize + bar repair")
print("==============================")


if len(sys.argv) < 3:
    print("usage: python clean_musicxml.py input.musicxml output.musicxml")
    sys.exit(1)


input_file = sys.argv[1]
output_file = sys.argv[2]


print("READ")
score = converter.parse(input_file)


# ----------------------------------------------------------
# remove bad notation
# ----------------------------------------------------------

print("remove voices")
for p in score.parts:
    for n in p.recurse().notes:
        if hasattr(n, "voices"):
            n.voices = None


print("remove chords")
for p in score.parts:
    for c in list(p.recurse().getElementsByClass('Chord')):
        n = note.Note(c.pitches[0])
        n.duration = c.duration
        c.activeSite.replace(c, n)


# ----------------------------------------------------------
# force 4/4
# ----------------------------------------------------------

print("force 4/4")

for p in score.parts:

    # remove old meters
    for ts in list(p.recurse().getElementsByClass('TimeSignature')):
        ts.activeSite.remove(ts)

    p.insert(0, meter.TimeSignature("4/4"))


# ----------------------------------------------------------
# quantize
# ----------------------------------------------------------

print("duration quantize")

grid = 0.25   # sixteenth note


for p in score.parts:

    for n in p.recurse().notesAndRests:

        q = round(n.duration.quarterLength / grid) * grid

        if q <= 0:
            q = grid

        n.duration.quarterLength = q



# ----------------------------------------------------------
# rebuild measures
# ----------------------------------------------------------

print("rebuild measures")

for p in score.parts:

    measures = p.getElementsByClass(stream.Measure)

    for m in measures:

        total = sum(
            x.duration.quarterLength
            for x in m.notesAndRests
        )


        # too long
        if total > 4:

            print(
                "repair long measure",
                m.number,
                total
            )


            diff = total - 4


            for n in reversed(list(m.notesAndRests)):

                if diff <= 0:
                    break


                if n.duration.quarterLength > diff:

                    n.duration.quarterLength -= diff
                    diff = 0

                else:

                    diff -= n.duration.quarterLength
                    n.duration.quarterLength = 0.25



        # too short
        total = sum(
            x.duration.quarterLength
            for x in m.notesAndRests
        )


        if total < 4:

            rest = note.Rest()
            rest.duration.quarterLength = 4-total
            m.append(rest)



# ----------------------------------------------------------
# remove unsupported duration
# ----------------------------------------------------------

print("remove unsupported duration")

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

    d = n.duration.quarterLength

    if d not in allowed:

        new = min(
            allowed,
            key=lambda x: abs(x-d)
        )

        n.duration.quarterLength = new



# ----------------------------------------------------------
# final check
# ----------------------------------------------------------

print("FINAL CHECK")


for m in score.parts[0].getElementsByClass(stream.Measure):

    length = sum(
        x.duration.quarterLength
        for x in m.notesAndRests
    )

    print(
        "Measure",
        m.number,
        length
    )


    if abs(length-4.0) > 0.01:

        print(
            "FIX",
            m.number
        )

        r = note.Rest()
        r.duration.quarterLength = max(
            0,
            4-length
        )

        m.append(r)



print("WRITE")

score.write(
    "musicxml",
    fp=output_file
)


print("==============================")
print("V34 DONE")
print(output_file)
print("==============================")