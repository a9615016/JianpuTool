import sys
from mido import MidiFile, MidiTrack, Message


print("======================")
print("MIDI CLEANER V29")
print("JIANPU MELODY MODE")
print("======================")


if len(sys.argv) < 3:
    print(
        "usage: python midi_cleaner.py input.mid output.mid"
    )
    sys.exit(1)



input_file = sys.argv[1]
output_file = sys.argv[2]



mid = MidiFile(input_file)



print(
    "ticks:",
    mid.ticks_per_beat
)



notes = []



# ==========================
# 收集 note
# ==========================

for track in mid.tracks:

    current_time = 0

    active = {}


    for msg in track:


        current_time += msg.time


        if msg.type == "note_on" and msg.velocity > 0:

            active[msg.note] = current_time



        elif msg.type in [
            "note_off"
        ] or (
            msg.type == "note_on"
            and msg.velocity == 0
        ):


            if msg.note in active:

                start = active.pop(
                    msg.note
                )


                duration = (
                    current_time-start
                )


                notes.append(
                    [
                        start,
                        duration,
                        msg.note,
                        msg.velocity
                    ]
                )



print(
    "original notes:",
    len(notes)
)



# ==========================
# 清理
# ==========================


clean = []



last_note = None



for n in sorted(notes):


    start, duration, pitch, vel = n



    # 太短刪除
    if duration < 20:
        continue



    # 限制音域
    if pitch < 36:
        continue


    if pitch > 96:
        continue



    # 同時間多音
    # 保留最高音旋律
    if last_note:

        if (
            start == last_note[0]
            and pitch != max(
                pitch,
                last_note[2]
            )
        ):
            continue



    clean.append(n)

    last_note = n




print(
    "clean notes:",
    len(clean)
)



# ==========================
# 建立新 MIDI
# ==========================


out = MidiFile(
    type=0,
    ticks_per_beat=mid.ticks_per_beat
)


track = MidiTrack()

out.tracks.append(track)



events = []



for start,duration,pitch,vel in clean:


    events.append(
        (
            start,
            Message(
                "note_on",
                note=pitch,
                velocity=vel,
                time=0
            )
        )
    )


    events.append(
        (
            start+duration,
            Message(
                "note_off",
                note=pitch,
                velocity=0,
                time=0
            )
        )
    )



events.sort(
    key=lambda x:x[0]
)



last_time = 0



for t,msg in events:


    msg.time = t-last_time

    last_time=t

    track.append(msg)



track.append(
    Message(
        "note_off",
        note=0,
        velocity=0,
        time=0
    )
)



out.save(
    output_file
)



print(
    "DONE:"
)


print(
    output_file
)import sys
from mido import MidiFile, MidiTrack, Message


print("======================")
print("MIDI CLEANER V29")
print("JIANPU MELODY MODE")
print("======================")


if len(sys.argv) < 3:
    print(
        "usage: python midi_cleaner.py input.mid output.mid"
    )
    sys.exit(1)



input_file = sys.argv[1]
output_file = sys.argv[2]



mid = MidiFile(input_file)



print(
    "ticks:",
    mid.ticks_per_beat
)



notes = []



# ==========================
# 收集 note
# ==========================

for track in mid.tracks:

    current_time = 0

    active = {}


    for msg in track:


        current_time += msg.time


        if msg.type == "note_on" and msg.velocity > 0:

            active[msg.note] = current_time



        elif msg.type in [
            "note_off"
        ] or (
            msg.type == "note_on"
            and msg.velocity == 0
        ):


            if msg.note in active:

                start = active.pop(
                    msg.note
                )


                duration = (
                    current_time-start
                )


                notes.append(
                    [
                        start,
                        duration,
                        msg.note,
                        msg.velocity
                    ]
                )



print(
    "original notes:",
    len(notes)
)



# ==========================
# 清理
# ==========================


clean = []



last_note = None



for n in sorted(notes):


    start, duration, pitch, vel = n



    # 太短刪除
    if duration < 20:
        continue



    # 限制音域
    if pitch < 36:
        continue


    if pitch > 96:
        continue



    # 同時間多音
    # 保留最高音旋律
    if last_note:

        if (
            start == last_note[0]
            and pitch != max(
                pitch,
                last_note[2]
            )
        ):
            continue



    clean.append(n)

    last_note = n




print(
    "clean notes:",
    len(clean)
)



# ==========================
# 建立新 MIDI
# ==========================


out = MidiFile(
    type=0,
    ticks_per_beat=mid.ticks_per_beat
)


track = MidiTrack()

out.tracks.append(track)



events = []



for start,duration,pitch,vel in clean:


    events.append(
        (
            start,
            Message(
                "note_on",
                note=pitch,
                velocity=vel,
                time=0
            )
        )
    )


    events.append(
        (
            start+duration,
            Message(
                "note_off",
                note=pitch,
                velocity=0,
                time=0
            )
        )
    )



events.sort(
    key=lambda x:x[0]
)



last_time = 0



for t,msg in events:


    msg.time = t-last_time

    last_time=t

    track.append(msg)



track.append(
    Message(
        "note_off",
        note=0,
        velocity=0,
        time=0
    )
)



out.save(
    output_file
)



print(
    "DONE:"
)


print(
    output_file
)