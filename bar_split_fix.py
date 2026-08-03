import sys
from music21 import converter, stream, note, chord, meter


input_file = sys.argv[1]
output_file = sys.argv[2]


print("Loading MusicXML")

score = converter.parse(input_file)


print("Fix measures")


# 強制 4/4
for part in score.parts:

    measures = part.getElementsByClass(stream.Measure)

    for m in measures:

        if m.timeSignature is None:
            m.insert(
                0,
                meter.TimeSignature("4/4")
            )


# 修復 duration
for element in score.recurse():

    if isinstance(element, (note.Note, note.Rest, chord.Chord)):

        ql = element.duration.quarterLength

        if ql <= 0:
            ql = 1.0

        element.duration.quarterLength = ql

        # 關鍵
        element.duration._type = None

        element.duration.type = element.duration.type


print("Make measures")


try:

    score.makeMeasures(
        inPlace=True
    )

except Exception as e:

    print(
        "makeMeasures skip:",
        e
    )


print("Writing")


score.write(
    "musicxml",
    fp=output_file
)


print(
    "DONE",
    output_file
)