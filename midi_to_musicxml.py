from music21 import converter, stream, meter, note, chord
import sys

print("==============================")
print("MIDI TO MUSICXML V2 (FIXED)")
print("==============================")

if len(sys.argv) < 3:
    print("python midi_to_musicxml.py input.mid output.musicxml")
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]

print("輸入:", input_file)
score = converter.parse(input_file)

print("remove chords")
for part in score.parts:
    for c in list(part.recurse().getElementsByClass(chord.Chord)):
        if c.pitches:
            n = note.Note(c.pitches[0])
            n.duration = c.duration
            c.activeSite.replace(c, n)

print("force 4/4")
for part in score.parts:
    part.insert(0, meter.TimeSignature("4/4"))

print("quantize")
for n in score.recurse().notesAndRests:
    q = max(0.25, round(float(n.duration.quarterLength)*4)/4)
    n.duration.quarterLength = q
    n.tie = None
    # 不要把 n.beams 設成 []，否則 music21 寫 MusicXML 會失敗

print("rebuild measures")
for part in score.parts:
    part.makeMeasures(inPlace=True)

print("寫入 MusicXML")
score.write("musicxml", fp=output_file)
print("完成:", output_file)
