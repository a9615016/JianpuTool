import sys
from music21 import converter, stream, note, chord, meter


input_file = sys.argv[1]
output_file = sys.argv[2]


score = converter.parse(input_file)


for part in score.parts:

    # 固定4/4
    part.insert(
        0,
        meter.TimeSignature("4/4")
    )

    # 移除 chord
    for c in part.recurse().getElementsByClass(chord.Chord):

        n = note.Note(
            c.root()
        )

        n.duration = c.duration

        c.activeSite.replace(
            c,
            n
        )


    # 所有音符重新量化
    for n in part.recurse().notesAndRests:

        try:

            n.duration.quarterLength = round(
                n.duration.quarterLength * 4
            ) / 4


        except:
            pass


# 重新建立小節
new_score = stream.Score()


for part in score.parts:

    p = stream.Part()

    measures = part.makeMeasures(
        inPlace=False
    )

    for m in measures:

        p.append(m)


    new_score.append(p)



new_score.makeNotation(
    inPlace=True
)


new_score.write(
    "musicxml",
    fp=output_file
)


print(
    "jianpu final prepare OK"
)