import sys
from music21 import converter, stream, meter, note, chord


print("================")
print("MIDI TO MUSICXML V3 FINAL JIANPU")
print("================")


if len(sys.argv) < 3:
    print("usage:")
    print("python midi_to_musicxml.py input.mid output.musicxml")
    sys.exit(1)


midi_file = sys.argv[1]
output_file = sys.argv[2]


print("輸入:")
print(midi_file)


# ==========================
# Read MIDI
# ==========================

print("讀取 MIDI...")

score = converter.parse(midi_file)



# ==========================
# Reduce to melody
# ==========================

print("整理旋律...")


new_score = stream.Score()


for part in score.parts:

    new_part = stream.Part()

    for n in part.flatten().notesAndRests:


        # remove chord
        if isinstance(n, chord.Chord):

            nn = note.Note(
                n.pitches[-1]
            )

            nn.duration = n.duration

            new_part.append(nn)


        else:

            new_part.append(n)



    new_score.append(new_part)



score = new_score



# ==========================
# Quantize duration
# ==========================

print("duration quantize")


allowed = [
    4,
    2,
    1,
    0.5,
    0.25
]


for n in score.recurse().notesAndRests:

    q = float(
        n.duration.quarterLength
    )

    closest = min(
        allowed,
        key=lambda x: abs(x-q)
    )

    n.duration.quarterLength = closest



# ==========================
# Split long notes
# ==========================

print("split long notes")


def split_long_notes(part):

    result = stream.Part()


    for n in part.flatten().notesAndRests:


        length = float(
            n.duration.quarterLength
        )


        if isinstance(n, note.Note):


            while length > 4:

                nn = note.Note(
                    n.pitch
                )

                nn.duration.quarterLength = 4

                result.append(nn)

                length -= 4



            if length > 0:

                nn = note.Note(
                    n.pitch
                )

                nn.duration.quarterLength = length

                result.append(nn)



        else:

            result.append(n)



    return result



fixed_score = stream.Score()


for part in score.parts:

    fixed_score.append(
        split_long_notes(part)
    )


score = fixed_score



# ==========================
# Rebuild measures
# ==========================

print("rebuild measures")


for part in score.parts:

    part.insert(
        0,
        meter.TimeSignature("4/4")
    )

    part.makeMeasures(
        inPlace=True
    )



# ==========================
# Check
# ==========================

print("CHECK MEASURES")


for i,m in enumerate(
    score.parts[0].getElementsByClass("Measure")
):

    print(
        "Measure",
        i+1,
        float(
            m.duration.quarterLength
        )
    )



# ==========================
# Write
# ==========================

print("寫入 MusicXML...")


score.write(
    "musicxml",
    fp=output_file
)


print("================")
print("完成:")
print(output_file)
print("================")