import sys
import music21


def clean_musicxml(input_file, output_file):

    print("CLEAN VERSION 20260725 MINIMAL")
    print("input:", input_file)

    score = music21.converter.parse(input_file)

    # ==========================
    # Remove Chords
    # ==========================
    print("remove chords")

    for c in list(score.recurse().getElementsByClass(music21.chord.Chord)):
        n = c.notes[-1]
        n.duration = c.duration
        c.activeSite.replace(c, n)

    # ==========================
    # Remove Grace Notes
    # ==========================
    print("remove grace notes")

    for n in list(score.recurse().notes):
        if n.duration.isGrace:
            n.activeSite.remove(n)

    # ==========================
    # Fix Duration
    # ==========================
    print("fix duration")

    for n in score.recurse().notesAndRests:
        if n.duration.quarterLength <= 0:
            n.duration.quarterLength = 0.25

    # ==========================
    # Remove Tuplets
    # ==========================
    print("remove tuplets")

    for n in score.recurse().notesAndRests:
        if n.duration.tuplets:
            ql = float(n.duration.quarterLength)
            n.duration.clear()
            n.duration.quarterLength = ql

    # ==========================
    # Write
    # ==========================
    print("write")

    score.write("musicxml", fp=output_file)

    print("done:", output_file)


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage:")
        print("python clean_musicxml.py input.musicxml output.musicxml")
        sys.exit(1)

    input_file = sys.argv[1]

    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        output_file = input_file.replace(".musicxml", "_clean.musicxml")

    clean_musicxml(input_file, output_file)