# clean_midi.py
# MIDI cleanup for BasicPitch -> MusicXML -> Jianpu

from mido import MidiFile, MidiTrack, Message, MetaMessage
import sys
import os


PPQ = 480
BAR_LENGTH = 4   # 4/4
GRID = 0.25      # quarter note subdivision


def quantize_time(ticks):
    beat = ticks / PPQ
    beat = round(beat / GRID) * GRID
    return int(round(beat * PPQ))


def clean_midi(input_file, output_file):

    mid = MidiFile(input_file)

    new_mid = MidiFile(
        type=1,
        ticks_per_beat=PPQ
    )

    for track in mid.tracks:

        new_track = MidiTrack()
        new_mid.tracks.append(new_track)

        abs_time = 0
        events = []

        for msg in track:

            abs_time += msg.time

            if msg.type == "note_on" and msg.velocity > 0:

                qtime = quantize_time(abs_time)

                events.append(
                    (
                        qtime,
                        msg.note,
                        msg.velocity
                    )
                )

        # 建立新的 MIDI
        last_time = 0

        for start, note, velocity in events:

            delta = start - last_time

            new_track.append(
                Message(
                    "note_on",
                    note=note,
                    velocity=velocity,
                    time=delta
                )
            )

            # 固定八分音符長度
            length = int(PPQ * 0.5)

            new_track.append(
                Message(
                    "note_off",
                    note=note,
                    velocity=0,
                    time=length
                )
            )

            last_time = start + length


        # 結尾
        new_track.append(
            MetaMessage(
                "end_of_track",
                time=0
            )
        )


    # 加入 4/4
    meta = MidiTrack()
    new_mid.tracks.insert(0, meta)

    meta.append(
        MetaMessage(
            "time_signature",
            numerator=4,
            denominator=4,
            clocks_per_click=24,
            notated_32nd_notes_per_beat=8,
            time=0
        )
    )

    meta.append(
        MetaMessage(
            "end_of_track",
            time=0
        )
    )


    new_mid.save(output_file)

    print("Clean MIDI saved:")
    print(output_file)



if __name__ == "__main__":

    if len(sys.argv) < 3:
        print(
            "Usage: python clean_midi.py input.mid output.mid"
        )
        sys.exit(1)


    clean_midi(
        sys.argv[1],
        sys.argv[2]
    )