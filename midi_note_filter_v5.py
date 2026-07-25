from music21 import converter, stream, note, chord
import sys


MIN_MIDI = 48      # 最低保留音(C3)
MAX_MIDI = 96      # 最高保留音(C7)
MIN_DURATION = 0.25

QUANTIZE = [
    4.0,
    3.0,
    2.0,
    1.5,
    1.0,
    0.75,
    0.5,
    0.25
]


def quantize(value):
    return min(QUANTIZE, key=lambda x: abs(x - value))


def choose_best(notes):
    def score(n):
        return (
            n.quarterLength * 100 +
            n.pitch.midi
        )

    return max(notes, key=score)


def filter_melody(input_file, output_file):

    print("Loading MIDI...")

    score = converter.parse(input_file)

    events = {}

    for e in score.recurse().notes:

        if isinstance(e, chord.Chord):

            p = max(e.pitches, key=lambda x: x.midi)

            n = note.Note(p)

            n.duration = e.duration

        else:

            n = note.Note(e.pitch)

            n.duration = e.duration

        midi = n.pitch.midi

        if midi < MIN_MIDI:
            continue

        if midi > MAX_MIDI:
            continue

        if n.quarterLength < MIN_DURATION:
            continue

        offset = round(float(e.offset), 4)

        events.setdefault(offset, []).append(n)

    melody = stream.Part()

    last_pitch = None
    last_note = None

    for offset in sorted(events.keys()):

        best = choose_best(events[offset])

        best.duration.quarterLength = quantize(
            float(best.quarterLength)
        )

        if (
            last_note is not None
            and last_pitch == best.pitch.midi
        ):

            last_note.duration.quarterLength += best.quarterLength

            continue

        melody.insert(offset, best)

        last_note = best
        last_pitch = best.pitch.midi

    out = stream.Score()

    out.insert(0, melody)

    out.write("midi", fp=output_file)

    print("Saved:", output_file)


if __name__ == "__main__":

    if len(sys.argv) != 3:

        print("Usage:")
        print("python midi_note_filter_v5.py input.mid output.mid")

        sys.exit(1)

    filter_melody(
        sys.argv[1],
        sys.argv[2]
    )