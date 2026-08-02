from music21 import converter

f=r"C:\Users\user\Desktop\JianpuTool\outputs\c7bf9621\fixed2.musicxml"

score=converter.parse(f)

part=score.parts[0]

for m in part.getElementsByClass('Measure')[:3]:
    print("\nMEASURE", m.number)

    for n in m.notesAndRests:
        print(
            n,
            "offset=", n.offset,
            "length=", n.duration.quarterLength,
            "tie=", n.tie
        )