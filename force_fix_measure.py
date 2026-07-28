from music21 import converter
import sys


src = sys.argv[1]
dst = sys.argv[2]


print("FORCE FIX MEASURE")


score = converter.parse(src)


for part in score.parts:

    part.makeMeasures(
        inPlace=True
    )


    for m in part.getElementsByClass('Measure'):

        total = m.duration.quarterLength


        if total > 4:

            print(
                "Fix measure",
                m.number,
                total
            )

            # 重新切拍
            m.splitAtDurations()


        elif total < 4:

            from music21 import note

            r = note.Rest()
            r.duration.quarterLength = 4-total
            m.append(r)


score.write(
    "musicxml",
    fp=dst
)


print("DONE")