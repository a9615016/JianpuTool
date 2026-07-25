import sys
import music21


def clean_musicxml(input_file, output_file):
    print("CLEAN VERSION 20260725")
    print("input:", input_file)

    score = music21.converter.parse(input_file)

    # ==========================
    # Remove Voices (保留音符)
    # ==========================
    print("remove voices")

    for part in score.parts:
        for measure in part.getElementsByClass(music21.stream.Measure):

            voices = list(measure.getElementsByClass(music21.stream.Voice))

            if not voices:
                continue

            new_notes = []

            for voice in voices:
                for element in voice.notesAndRests:
                    new_notes.append(element)

            measure.removeByClass(music21.stream.Voice)

            offset = 0

            for n in new_notes:
                n.offset = offset
                measure.insert(offset, n)
                offset += n.quarterLength

    # ==========================
    # Remove Chords
    # ==========================
    print("remove chords")

    for chord in list(score.recurse().getElementsByClass(music21.chord.Chord)):
        note = chord.notes[-1]
        note.duration = chord.duration
        chord.activeSite.replace(chord, note)

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

            if ql <= 0:
                ql = 0.25

            n.duration.quarterLength = ql

    # ==========================
    # Cleanup
    # ==========================
    print("final cleanup")

    score.makeMeasures(inPlace=True)

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