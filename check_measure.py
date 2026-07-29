from music21 import converter
import sys


xml = sys.argv[1]

score = converter.parse(xml)


for part in score.parts:

    for i, m in enumerate(part.getElementsByClass("Measure")):

        length = 0

        for n in m.notesAndRests:
            length += n.duration.quarterLength

        print(
            "Measure",
            i+1,
            float(length)
        )