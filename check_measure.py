from music21 import converter
import sys


file = sys.argv[1]

score = converter.parse(file)


for part in score.parts:

    print("PART")

    for i, m in enumerate(
        part.getElementsByClass("Measure")
    ):

        total = 0

        for n in m.notesAndRests:
            total += n.duration.quarterLength


        print(
            "Measure",
            i+1,
            total
        )