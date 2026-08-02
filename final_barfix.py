from music21 import converter, note


src = r"C:\Users\user\Desktop\JianpuTool\outputs\c7bf9621\jianpu_ready3.musicxml"

out = r"C:\Users\user\Desktop\JianpuTool\outputs\c7bf9621\final.musicxml"


score = converter.parse(src)


for part in score.parts:

    for m in part.getElementsByClass("Measure"):

        new_elements = []

        total = 0

        for n in m.notesAndRests:

            length = float(n.duration.quarterLength)

            # 限制到16分音符
            length = round(length * 4) / 4

            if length <= 0:
                continue

            n.duration.quarterLength = length

            # 清掉特殊連結
            n.tie = None

            new_elements.append(n)

            total += length


        # 補滿4拍
        if total < 4:

            r = note.Rest()

            r.duration.quarterLength = 4 - total

            new_elements.append(r)


        m.clear()

        for n in new_elements:
            m.append(n)



score.write(
    "musicxml",
    fp=out
)


print(out)