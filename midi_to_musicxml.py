from music21 import converter, stream, note, chord, meter, tempo
import sys
import os


print("==============================")
print("MIDI TO MUSICXML V2")
print("JIANPU_LY COMPATIBLE")
print("==============================")


if len(sys.argv) < 3:
    print("使用:")
    print("python midi_to_musicxml_v2.py input.mid output.musicxml")
    sys.exit(1)


input_midi = sys.argv[1]
output_xml = sys.argv[2]


print("讀取 MIDI:")
print(input_midi)


# =========================
# Load MIDI
# =========================

score = converter.parse(input_midi)


print("整理音符...")


# =========================
# 建立新 Score
# =========================

new_score = stream.Score()


part = stream.Part()


# 4/4
part.append(meter.TimeSignature("4/4"))


# tempo
part.append(tempo.MetronomeMark(number=80))


notes = []


# =========================
# Extract melody only
# =========================

for element in score.recurse():

    if isinstance(element, note.Note):

        n = note.Note(element.pitch)

        dur = element.duration.quarterLength


        # remove tiny notes
        if dur < 0.125:
            continue


        # quantize
        allowed = [
            0.25,
            0.5,
            0.75,
            1.0,
            1.5,
            2.0,
            3.0,
            4.0
        ]

        q = min(
            allowed,
            key=lambda x: abs(x-dur)
        )


        n.duration.quarterLength = q


        notes.append(n)



    elif isinstance(element, chord.Chord):

        # chord 只取最高音

        n = note.Note(
            element.sortAscending().notes[-1].pitch
        )


        dur = element.duration.quarterLength


        if dur < 0.125:
            continue


        allowed = [
            0.25,
            0.5,
            0.75,
            1.0,
            1.5,
            2.0,
            3.0,
            4.0
        ]


        q = min(
            allowed,
            key=lambda x: abs(x-dur)
        )


        n.duration.quarterLength = q

        notes.append(n)



print("音符數:", len(notes))


# =========================
# Rebuild measures
# =========================


measure = stream.Measure()

length = 0


measure_no = 1


for n in notes:

    dur = n.duration.quarterLength


    # 如果超過4拍
    if length + dur > 4:

        remain = 4 - length


        if remain > 0:

            n1 = n.clone()
            n1.duration.quarterLength = remain
            measure.append(n1)


        part.append(measure)


        print(
            "Measure",
            measure_no,
            4.0
        )


        measure_no += 1


        measure = stream.Measure()


        remain2 = dur - remain


        if remain2 > 0:

            n2 = n.clone()
            n2.duration.quarterLength = remain2

            measure.append(n2)

            length = remain2

        else:
            length = 0


    else:

        measure.append(n)

        length += dur



# final measure

if len(measure.notes) > 0:

    while length < 4:

        r = note.Rest()

        r.duration.quarterLength = min(
            4-length,
            0.25
        )

        measure.append(r)

        length += r.duration.quarterLength


    part.append(measure)



new_score.append(part)



print("重新量化完成")


# =========================
# Remove voices/chords
# =========================


for p in new_score.parts:

    for m in p.getElementsByClass(
        stream.Measure
    ):

        for n in list(m.notes):

            if isinstance(n, chord.Chord):

                nn = note.Note(
                    n.notes[-1].pitch
                )

                nn.duration = n.duration

                n.activeSite.replace(
                    n,
                    nn
                )



print("寫入 MusicXML")


# =========================
# Write
# =========================

new_score.write(
    "musicxml",
    fp=output_xml
)


print("==============================")
print("完成:")
print(output_xml)
print("==============================")