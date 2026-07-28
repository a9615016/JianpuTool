from music21 import converter, note, stream
import sys


src = sys.argv[1]
dst = sys.argv[2]


print("================")
print("FORCE FIX MEASURE V2")
print("================")


score = converter.parse(src)


for part in score.parts:

    print("Processing part")

    # 重新建立單聲部
    flat_notes = []

    for n in part.flatten().notesAndRests:
        flat_notes.append(n)


    new_part = stream.Part()


    for n in flat_notes:
        new_part.append(n)


    # 重新切小節
    new_part.makeMeasures(
        inPlace=True
    )


    for m in new_part.getElementsByClass("Measure"):

        length = m.duration.quarterLength


        print(
            "Measure",
            m.number,
            length
        )


        # 超過4拍處理
        if length > 4:

            print(
                "WARNING too long:",
                m.number,
                length
            )


        # 不足補休止符
        if length < 4:

            r = note.Rest()

            r.duration.quarterLength = 4 - length

            m.append(r)


    # 回寫
    part.clear()

    for element in new_part:

        part.append(element)



print("FINAL CHECK")


for part in score.parts:

    for m in part.getElementsByClass("Measure"):

        print(
            "Measure",
            m.number,
            m.duration.quarterLength
        )


score.write(
    "musicxml",
    fp=dst
)


print("DONE")
print(dst)