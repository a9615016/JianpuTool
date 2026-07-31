from music21 import converter, note
import sys

src = sys.argv[1]
dst = sys.argv[2]

score = converter.parse(src)

count = 0

for n in score.recurse().notes:
    if isinstance(n, note.Note):
        while n.pitch.octave < 2:
            n.pitch.octave += 1
            count += 1

        while n.pitch.octave > 6:
            n.pitch.octave -= 1
            count += 1

score.write("musicxml", fp=dst)

print("Fixed notes:", count)
print("Saved:", dst)