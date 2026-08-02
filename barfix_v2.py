from music21 import converter, stream, meter, note

src = r"C:\Users\user\Desktop\JianpuTool\outputs\c7bf9621\music.musicxml"
out = r"C:\Users\user\Desktop\JianpuTool\outputs\c7bf9621\fixed2.musicxml"

score = converter.parse(src)

new_score = stream.Score()

for part in score.parts:

    new_part = stream.Part()
    new_part.insert(0, meter.TimeSignature("4/4"))

    measure_no = 1
    current = stream.Measure(number=measure_no)

    beat = 0.0

    for n in part.flatten().notesAndRests:

        length = float(n.duration.quarterLength)

        # 16分音符量化
        length = max(0.25, round(length * 4) / 4)

        if beat + length > 4.0:

            if beat < 4.0:
                r = note.Rest()
                r.duration.quarterLength = 4.0 - beat
                current.append(r)

            new_part.append(current)

            measure_no += 1
            current = stream.Measure(number=measure_no)
            beat = 0.0

        n.duration.quarterLength = length
        

        current.append(n)
        beat += length

    if beat < 4.0:
        r = note.Rest()
        r.duration.quarterLength = 4.0 - beat
        r.duration.quarterLength = 4.0 - beat
        current.append(r)

    new_part.append(current)

    new_score.append(new_part)

new_score.write("musicxml", fp=out)

print(out)