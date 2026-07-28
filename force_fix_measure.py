from music21 import converter, note, stream
import sys


src = sys.argv[1]
dst = sys.argv[2]


print("================")
print("FORCE FIX MEASURE V25")
print("================")


score = converter.parse(src)


for part in score.parts:

    part.makeMeasures(inPlace=True)


    for m in part.getElementsByClass("Measure"):

        total = m.duration.quarterLength


        print(
            "Measure",
            m.number,
            total
        )


        # 超過4拍
        if total > 4:

            print(
                "TRIM",
                m.number,
                total
            )


            current = 0


            for n in list(m.notesAndRests):

                d = n.duration.quarterLength


                if current + d > 4:

                    remain = 4-current


                    if remain > 0:
                        n.duration.quarterLength = remain
                        current = 4

                    else:
                        m.remove(n)

                else:
                    current += d



        # 不足4拍補休止
        total = m.duration.quarterLength


        if total < 4:

            r = note.Rest()

            r.duration.quarterLength = (
                4-total
            )

            m.append(r)



    # 重新整理
    part.makeMeasures(
        inPlace=True
    )



print("================")
print("FINAL CHECK")
print("================")


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