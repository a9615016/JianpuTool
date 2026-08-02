from music21 import converter, note

f=r"C:\Users\user\Desktop\JianpuTool\outputs\c7bf9621\final2.musicxml"

score=converter.parse(f)

notes=score.flatten().notes

print("NOTE COUNT =",len(notes))

for n in notes[:20]:
    print(n, n.duration.quarterLength)