from music21 import converter, meter, note, stream

src = r"C:\Users\user\Desktop\JianpuTool\outputs\c7bf9621\music.musicxml"
out = r"C:\Users\user\Desktop\JianpuTool\outputs\c7bf9621\fixed.musicxml"

score = converter.parse(src)

for part in score.parts:
    part.removeByClass('TimeSignature')
    part.insert(0, meter.TimeSignature('4/4'))

    measures = part.makeMeasures()

    for m in measures:
        dur = m.duration.quarterLength

        # 超過4拍，截斷
        if dur > 4:
    remain = 4.0
    new_elements = []

    for n in m.notesAndRests:
        if remain <= 0:
            break

        length = n.duration.quarterLength

        if length <= remain:
            new_elements.append(n)
            remain -= length
        else:
            n.duration.quarterLength = remain
            new_elements.append(n)
            remain = 0

    m.clear()
    for n in new_elements:
        m.append(n)

        # 不足4拍，補休止
        dur = m.duration.quarterLength
        if dur < 4:
            r = note.Rest()
            r.duration.quarterLength = 4 - dur
            m.append(r)

score.write("musicxml", fp=out)

print(out)