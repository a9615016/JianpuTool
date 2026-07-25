from music21 import converter, stream, note, chord
import sys


MIN_DURATION = 0.125


def extract_melody(input_file, output_file):

    print("Loading:", input_file)

    score = converter.parse(input_file)

    # 找音符最多的 Part
    if len(score.parts) > 0:

        best_part = max(
            score.parts,
            key=lambda p: len(list(p.recurse().notes))
        )

    else:

        best_part = score

    melody = stream.Part()
    events = {}

    # 收集音符
    for n in best_part.recurse().notes:

        if isinstance(n, chord.Chord):

            highest = max(n.pitches, key=lambda x: x.midi)

            new_note = note.Note(highest)

            new_note.duration = n.duration

        else:

            new_note = note.Note(n.pitch)

            new_note.duration = n.duration

        if float(new_note.quarterLength) < MIN_DURATION:
            continue

        offset = round(float(n.offset), 4)

        # 同一時間點保留音高最高者
        if offset not in events:
            events[offset] = new_note
        else:
            if new_note.pitch.midi > events[offset].pitch.midi:
                events[offset] = new_note

    # 依時間輸出
    for offset in sorted(events.keys()):
        melody.insert(offset, events[offset])

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