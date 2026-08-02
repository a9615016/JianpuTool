from music21 import converter

f=r"C:\Users\user\Desktop\JianpuTool\outputs\c7bf9621\final.musicxml"

score=converter.parse(f)

print(
    "NOTE COUNT =",
    len(score.flatten().notes)
)