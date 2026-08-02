from music21 import converter

f = r"C:\Users\user\Desktop\JianpuTool\outputs\c7bf9621\rebuild44_v2.musicxml"

score = converter.parse(f)

for m in score.parts[0].getElementsByClass('Measure')[:10]:
    print(
        "Measure",
        m.number,
        "duration=",
        m.duration.quarterLength
    )