from music21 import converter, stream, note, chord
import sys


def filter_melody(input_midi, output_midi):
    score = converter.parse(input_midi)

    melody = stream.Part()
    melody.id = "Melody"

    events = {}

    # 收集所有音符
    for n in score.recurse().notes:
        offset = round(float(n.offset), 4)

        if isinstance(n, chord.Chord):
            p = max(n.pitches, key=lambda x: x.midi)
            new_note = note.Note(p)
        else:
            new_note = note.Note(n.pitch)

        new_note.duration = n.duration

        # 忽略太短的音
        if new_note.quarterLength < 0.1:
            continue

        events.setdefault(offset, []).append(new_note)

    last_pitch = None

    for offset in sorted(events.keys()):

        # 每個時間點保留最高音
        best = max(events[offset], key=lambda x: x.pitch.midi)

        # 合併重複音
        if last_pitch == best.pitch.midi:
            continue

        melody.insert(offset, best)
        last_pitch = best.pitch.midi

    out = stream.Score()
    out.insert(0, melody)

    out.write("midi", fp=output_midi)

    print("Saved:", output_midi)


if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("Usage:")
        print("python midi_note_filter_v4.py input.mid output.mid")
        sys.exit(1)

    filter_melody(sys.argv[1], sys.argv[2])