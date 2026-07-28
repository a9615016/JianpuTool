from music21 import converter
from music21 import note
from music21 import stream
import sys


print("================")
print("FORCE FIX MEASURE V2")
print("================")


src=sys.argv[1]
dst=sys.argv[2]


score=converter.parse(src)



for part in score.parts:


    print("PROCESS PART")


    # 重新切小節
    part.makeMeasures(
        inPlace=True
    )


    newPart=stream.Part()


    for m in part.getElementsByClass("Measure"):


        current=0


        notes=list(
            m.notesAndRests
        )


        newMeasure=stream.Measure(
            number=m.number
        )


        for n in notes:


            dur=float(
                n.duration.quarterLength
            )


            # 強制量化
            dur=round(
                dur*4
            )/4


            if dur<=0:
                continue


            if dur>1:
                dur=1


            n.duration.quarterLength=dur


            newMeasure.append(n)



        total=float(
            newMeasure.duration.quarterLength
        )


        print(
            "Measure",
            m.number,
            total
        )


        # 補滿4拍

        if total < 4:

            r=note.Rest()

            r.duration.quarterLength=4-total

            newMeasure.append(r)


        newPart.append(
            newMeasure
        )



    part.replace(
        part.recurse().getElementsByClass("Measure"),
        newPart
    )



score.write(
    "musicxml",
    fp=dst
)


print("DONE")