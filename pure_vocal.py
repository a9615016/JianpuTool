from music21 import converter, stream, note, meter
import sys

src = sys.argv[1]
dst = sys.argv[2]

score = converter.parse(src)

out = stream.Score()
part = stream.Part()

part.append(meter.TimeSignature("4/4"))

for n in score.recurse().notesAndRests:
    if isinstance(n, note.Note):
        new = note.Note(n.pitch)
        new.duration = n.duration
        part.append(new)

    elif isinstance(n, note.Rest):
        new = note.Rest()
        new.duration = n.duration
        part.append(new)

out.append(part)

out.write("musicxml", fp=dst)

print("pure vocal saved:", dst)