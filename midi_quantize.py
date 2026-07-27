from mido import MidiFile, MidiTrack
import sys
import os

VERSION = "MIDI QUANTIZE V2"


def quantize_tick(tick, grid):
    return int(round(tick / grid) * grid)


def clean_midi(input_file, output_file):

    print(VERSION)
    print("input:", input_file)

    mid = MidiFile(input_file)

    grid = max(1, mid.ticks_per_beat // 4)   # 16分音符

    print("ticks_per_beat:", mid.ticks_per_beat)
    print("grid:", grid)

    new_mid = MidiFile(
        ticks_per_beat=mid.ticks_per_beat
    )

    for track in mid.tracks:

        abs_time = 0
        events = []

        # 收集事件（絕對時間）
        for msg in track:

            abs_time += msg.time

            if msg.type in ("note_on", "note_off"):
                events.append(
                    (
                        quantize_tick(abs_time, grid),
                        msg
                    )
                )

        # 按時間排序
        events.sort(key=lambda x: x[0])

        new_track = MidiTrack()

        last_time = 0

        for abs_tick, msg in events:

            delta = abs_tick - last_time

            if delta < 0:
                delta = 0

            new_track.append(
                msg.copy(time=delta)
            )

            last_time = abs_tick

        new_mid.tracks.append(new_track)

    new_mid.save(output_file)

    print("done:")
    print(output_file)


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("python midi_quantize.py input.mid output.mid")
        sys.exit(1)

    inp = sys.argv[1]

    if len(sys.argv) >= 3:
        out = sys.argv[2]
    else:
        out = os.path.splitext(inp)[0] + "_clean.mid"

    clean_midi(inp, out)