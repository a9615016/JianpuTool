from music21 import converter, stream, note, chord
import sys

MIN_MIDI = 48          # C3
MAX_MIDI = 96          # C7
MIN_DURATION = 0.25


def extract_melody(input_file, output_file):

    print("Loading:", input_file)

    score = converter.parse(input_file)

    # 找音符最多的 Part
    if score.parts:
        part = max(score.parts, key=lambda p: len(list(p.recurse().notes)))
    else:
        part = score

    melody = stream.Part()

    events = {}

    for n in part.recurse().notes:

        if isinstance(n, chord.Chord):
            p = max(n.pitches, key=lambda x: x.midi)
            new = note.Note(p)
            new.duration = n.duration
        else:
            new = note.Note(n.pitch)
            new.duration = n.duration

        midi = new.pitch.midi

        if midi < MIN_MIDI:
            continue

        if midi > MAX_MIDI:
            continue

        if new.quarterLength < MIN_DURATION:
            continue

        offset = round(float(n.offset), 4)

        score_value = (
            new.quarterLength * 100
            + midi
        )

        if offset not in events:
            events[offset] = (score_value, new)
        else:
            if score_value > events[offset][0]:
                events[offset] = (score_value, new)

    last_pitch = None
    last_note = None

    for offset in sorted(events.keys()):

        n = events[offset][1]

        if last_note and last_pitch == n.pitch.midi:

            last_note.duration.quarterLength += n.quarterLength

        else:

            melody.insert(offset, n)

            last_note = n
            last_pitch = n.pitch.midi

    out = stream.Score()
    out.insert(0, melody)

    out.write("midi", fp=output_file)

    print("Saved:", output_file)


if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("Usage:")
        print("python melody_extractor.py input.mid output.mid")
        sys.exit(1)

    extract_melody(
        sys.argv[1],
        sys.argv[2]
    )