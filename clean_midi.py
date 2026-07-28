from pathlib import Path
import sys
import mido


print("==============================")
print("CLEAN MIDI V2 BASICPITCH FINAL")
print("==============================")


if len(sys.argv) < 3:
    print("Usage:")
    print("python clean_midi.py input.mid output.mid")
    sys.exit(1)


input_mid = sys.argv[1]
output_mid = sys.argv[2]


print("READ MIDI")
print(input_mid)


mid = mido.MidiFile(input_mid)


ticks = mid.ticks_per_beat


# ==========================
# quantize 設定
# ==========================

# 16分音符格
GRID = ticks / 4


def quantize(t):
    return int(round(t / GRID) * GRID)



# ==========================
# 收集 note
# ==========================

notes = []

current_time = 0

active = {}


for track in mid.tracks:

    current_time = 0

    for msg in track:

        current_time += msg.time


        if msg.type == "note_on" and msg.velocity > 0:

            active[msg.note] = (
                current_time,
                msg.velocity
            )


        elif msg.type in ["note_off","note_on"]:

            if msg.note in active:

                start, vel = active[msg.note]

                end = current_time

                duration = end-start


                # 太短刪除
                if duration >= ticks/8:

                    notes.append(
                        {
                            "note":msg.note,
                            "start":start,
                            "end":end,
                            "vel":vel
                        }
                    )


                del active[msg.note]



print("NOTES BEFORE:",len(notes))


# ==========================
# quantize
# ==========================

for n in notes:

    n["start"] = quantize(n["start"])
    n["end"]   = quantize(n["end"])


    if n["end"] <= n["start"]:
        n["end"] = n["start"] + GRID



# ==========================
# 排序
# ==========================

notes.sort(
    key=lambda x:x["start"]
)



print("NOTES AFTER:",len(notes))



# ==========================
# 建立新 MIDI
# ==========================


out = mido.MidiFile(
    ticks_per_beat=ticks
)


track = mido.MidiTrack()

out.tracks.append(track)



last = 0


for n in notes:

    delta = n["start"] - last

    track.append(
        mido.Message(
            "note_on",
            note=n["note"],
            velocity=n["vel"],
            time=max(0,int(delta))
        )
    )


    duration = n["end"] - n["start"]


    track.append(
        mido.Message(
            "note_off",
            note=n["note"],
            velocity=0,
            time=int(duration)
        )
    )


    last = n["end"]



track.append(
    mido.MetaMessage(
        "end_of_track",
        time=0
    )
)



out.save(output_mid)



print("==============================")
print("DONE")
print(output_mid)
print("==============================")