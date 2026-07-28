import sys
import mido


print("==============================")
print("CLEAN MIDI V2.1 BASICPITCH")
print("==============================")


if len(sys.argv) < 3:
    print(
        "Usage: python clean_midi.py input.mid output.mid"
    )
    sys.exit(1)


input_mid = sys.argv[1]
output_mid = sys.argv[2]


print("INPUT:")
print(input_mid)


mid = mido.MidiFile(input_mid)


ticks = mid.ticks_per_beat


# 16分音符量化
GRID = ticks // 4


def quantize(t):
    return int(round(t / GRID) * GRID)



notes = []


tempo_msgs = []
time_msgs = []


active = {}


# ==========================
# 讀 MIDI
# ==========================

for track in mid.tracks:

    current = 0


    for msg in track:

        current += msg.time


        if msg.type == "set_tempo":

            tempo_msgs.append(
                msg
            )


        if msg.type == "time_signature":

            time_msgs.append(
                msg
            )


        if msg.type == "note_on" and msg.velocity > 0:

            active[msg.note] = {
                "start": current,
                "velocity": msg.velocity
            }


        elif (
            msg.type == "note_off"
            or (
                msg.type == "note_on"
                and msg.velocity == 0
            )
        ):

            if msg.note in active:

                data = active.pop(
                    msg.note
                )


                duration = current - data["start"]


                # 刪除雜訊
                if duration >= ticks / 8:

                    notes.append(
                        {
                            "note": msg.note,
                            "start": data["start"],
                            "end": current,
                            "velocity": data["velocity"]
                        }
                    )



print(
    "NOTES BEFORE:",
    len(notes)
)



# ==========================
# Quantize
# ==========================

for n in notes:

    n["start"] = quantize(
        n["start"]
    )

    n["end"] = quantize(
        n["end"]
    )


    if n["end"] <= n["start"]:

        n["end"] = (
            n["start"]
            +
            GRID
        )



# ==========================
# 去除重疊
# ==========================

notes.sort(
    key=lambda x: (
        x["start"],
        x["note"]
    )
)


last_end = {}


clean = []


for n in notes:

    pitch = n["note"]


    if pitch in last_end:

        if n["start"] < last_end[pitch]:

            n["start"] = last_end[pitch]


            if n["end"] <= n["start"]:

                continue


    last_end[pitch] = n["end"]

    clean.append(n)



notes = clean


print(
    "NOTES AFTER:",
    len(notes)
)



# ==========================
# 建立新 MIDI
# ==========================


out = mido.MidiFile(
    ticks_per_beat=ticks
)


track = mido.MidiTrack()

out.tracks.append(track)



# tempo

for msg in tempo_msgs:

    track.append(
        msg.copy(
            time=0
        )
    )


# 拍號

for msg in time_msgs:

    track.append(
        msg.copy(
            time=0
        )
    )



events = []


for n in notes:

    events.append(
        (
            n["start"],
            mido.Message(
                "note_on",
                note=n["note"],
                velocity=n["velocity"],
                time=0
            )
        )
    )


    events.append(
        (
            n["end"],
            mido.Message(
                "note_off",
                note=n["note"],
                velocity=0,
                time=0
            )
        )
    )



events.sort(
    key=lambda x:x[0]
)



last = 0


for t,msg in events:

    msg.time = int(
        t-last
    )

    track.append(msg)

    last = t



track.append(
    mido.MetaMessage(
        "end_of_track",
        time=0
    )
)



out.save(
    output_mid
)



print("==============================")
print("DONE")
print(output_mid)
print("==============================")