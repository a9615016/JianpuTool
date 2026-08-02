from music21 import converter

f = r"outputs\c7bf9621\force44_final.musicxml"

score = converter.parse(f)

for p in score.parts:
    for m in p.getElementsByClass("Measure"):
        print(
            "Measure",
            m.number,
            "duration=",
            m.duration.quarterLength,
            "barDuration=",
            m.barDuration.quarterLength
        )