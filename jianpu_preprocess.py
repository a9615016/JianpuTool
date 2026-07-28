from music21 import converter
from music21 import stream
from music21 import note
import sys


print("====================")
print("JIANPU PREPROCESS FINAL")
print("====================")


src = sys.argv[1]
dst = sys.argv[2]


score = converter.parse(src)


out_score = stream.Score()


for part in score.parts:

    new_part = stream.Part()

    measures = []

    current = stream.Measure()

    beat = 0


    for n in part.recurse().notesAndRests:


        dur = float(
            n.duration.quarterLength
        )


        # 量化到16分音符
        dur = round(dur * 4) / 4


        if dur <= 0:
            continue


        # 拆跨小節

        remain = dur


        while remain > 0:


            space = 4 - beat


            use = min(
                remain,
                space
            )


            if isinstance(n, note.Note):

                nn = note.Note(
                    n.pitch
                )

            else:

                nn = note.Rest()



            nn.duration.quarterLength = use


            current.append(nn)


            beat += use
            remain -= use



            if beat >= 4:


                measures.append(
                    current
                )


                current = stream.Measure()

                beat = 0



    # 最後補滿

    if beat > 0:


        r = note.Rest()

        r.duration.quarterLength = 4-beat

        current.append(r)

        measures.append(current)



    for i,m in enumerate(measures):

        m.number=i+1


        print(
            "Measure",
            i+1,
            float(m.duration.quarterLength)
        )


        new_part.append(m)



    out_score.insert(
        0,
        new_part
    )



print("WRITE")


out_score.write(
    "musicxml",
    fp=dst
)


print("DONE")