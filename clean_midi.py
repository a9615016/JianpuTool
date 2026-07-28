from mido import MidiFile, MidiTrack, Message, MetaMessage
import sys


print("==============================")
print("CLEAN MIDI V1")
print("BASIC PITCH JIANPU FIX")
print("==============================")


if len(sys.argv) < 3:
    print(
        "python clean_midi.py input.mid output.mid"
    )
    sys.exit()


input_file = sys.argv[1]
output_file = sys.argv[2]


print("read midi")

mid = MidiFile(input_file)


ticks = mid.ticks_per_beat


print("ticks per beat:", ticks)


# =========================
# collect notes
# =========================

notes = []

current_time = 0

active = {}


print("collect notes")


for track in mid.tracks:

    current_time = 0

    for msg in track:

        current_time += msg.time


        if msg.type == "note_on" and msg.velocity > 0:

            active[msg.note] = (
                current_time,
                msg.velocity
            )


        elif (
            msg.type == "note_off"
            or (
                msg.type == "note_on"
                and msg.velocity == 0
            )
        ):

            if msg.note in active:

                start, velocity = active.pop(
                    msg.note
                )

                duration = (
                    current_time - start
                )


                notes.append(
                    [
                        msg.note,
                        start,
                        duration,
                        velocity
                    ]
                )



print(
    "notes:",
    len(notes)
)



# =========================
# remove short notes
# =========================

print("remove short notes")


clean = []


min_length = ticks / 8


for n in notes:

    if n[2] >= min_length:

        clean.append(n)



notes = clean



# =========================
# quantize
# =========================

print("quantize")


grid = ticks / 4


for n in notes:


    # start

    n[1] = round(
        n[1] / grid
    ) * grid



    # duration

    n[2] = round(
        n[2] / grid
    ) * grid



    if n[2] <= 0:

        n[2] = grid



# =========================
# remove overlap
# =========================

print("remove overlap")


notes.sort(
    key=lambda x:x[1]
)


last_end = -1


final_notes=[]


for n in notes:


    if n[1] < last_end:

        n[1] = last_end



    final_notes.append(n)


    last_end = (
        n[1]+n[2]
    )



notes = final_notes



# =========================
# create midi
# =========================

print("write midi")


out = MidiFile(
    ticks_per_beat=ticks
)


track = MidiTrack()

out.tracks.append(track)



# tempo

track.append(
    MetaMessage(
        "set_tempo",
        tempo=500000,
        time=0
    )
)



events=[]


for pitch,start,duration,velocity in notes:


    events.append(
        (
            start,
            Message(
                "note_on",
                note=int(pitch),
                velocity=int(velocity),
                time=0
            )
        )
    )


    events.append(
        (
            start+duration,
            Message(
                "note_off",
                note=int(pitch),
                velocity=0,
                time=0
            )
        )
    )



events.sort(
    key=lambda x:x[0]
)



last=0


for t,msg in events:

    msg.time=int(
        t-last
    )

    track.append(msg)

    last=t



track.append(
    MetaMessage(
        "end_of_track",
        time=0
    )
)



out.save(
    output_file
)



print("================")
print("DONE")
print(output_file)
print("================")