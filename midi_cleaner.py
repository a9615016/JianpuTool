import sys
import mido


def clean_midi(src, dst):

    print("================")
    print("MIDI CLEANER V29")
    print("================")

    mid = mido.MidiFile(src)

    out = mido.MidiFile(
        ticks_per_beat=mid.ticks_per_beat
    )

    for track in mid.tracks:

        new_track = mido.MidiTrack()

        last_note = None
        last_time = 0

        for msg in track:

            if msg.type == "note_on":

                # 移除重複音
                if msg.note == last_note:
                    continue

                last_note = msg.note


            # 移除超短事件
            if msg.time < 5:
                msg.time = 5


            new_track.append(msg)


        out.tracks.append(new_track)


    out.save(dst)

    print("MIDI CLEAN DONE")
    print(dst)


if __name__ == "__main__":

    clean_midi(
        sys.argv[1],
        sys.argv[2]
    )