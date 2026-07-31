import sys
from music21 import converter, stream, note, chord, meter

def analyze(path):
    print("FILE:", path)

    score = converter.parse(path)

    print("\n=== PARTS ===")
    print("Parts:", len(score.parts))

    print("\n=== TIME SIGNATURE ===")
    ts = score.recurse().getElementsByClass(meter.TimeSignature)
    for t in ts:
        print(t.ratioString)

    print("\n=== MEASURES ===")
    measures = score.makeMeasures().recurse().getElementsByClass('Measure')
    print("Measures:", len(measures))

    print("\n=== NOTES ===")
    notes = score.recurse().notes

    note_count = 0
    chord_count = 0

    for n in notes:
        if isinstance(n, note.Note):
            note_count += 1
        elif isinstance(n, chord.Chord):
            chord_count += 1

    print("Notes:", note_count)
    print("Chords:", chord_count)

    print("\n=== VOICE ===")
    voices = score.recurse().getElementsByClass('Voice')
    print("Voices:", len(voices))

    print("\n=== DONE ===")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyzer.py file.musicxml")
        sys.exit()

    analyze(sys.argv[1])