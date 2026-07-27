import sys
import mido
from mido import MidiFile, MidiTrack, Message


print("======================")
print("MIDI CLEANER V29")
print("JIANPU MELODY MODE")
print("======================")


# 16分音符量化
GRID = 120


def quantize_tick(tick):

    return round(
        tick / GRID
    ) * GRID



def clean_midi(
    input_file,
    output_file
):


    print("READ MIDI")
    print(input_file)


    mid = MidiFile(
        input_file
    )


    ticks = mid.ticks_per_beat


    print(
        "ticks:",
        ticks
    )


    events = []


    # 收集 note

    for track in mid.tracks:


        abs_time = 0


        active = {}


        for msg in track:


            abs_time += msg.time



            if msg.type == "note_on" and msg.velocity > 0:


                active[msg.note] = (
                    abs_time,
                    msg.velocity
                )



            elif (
                msg.type == "note_off"
                or
                (
                    msg.type=="note_on"
                    and msg.velocity==0
                )
            ):


                if msg.note in active:


                    start, vel = active.pop(
                        msg.note
                    )


                    end = abs_time


                    events.append(
                        {
                            "note":msg.note,
                            "start":start,
                            "end":end,
                            "velocity":vel
                        }
                    )



    print(
        "original notes:",
        len(events)
    )



    # -----------------------
    # 修正 duration
    # -----------------------

    cleaned=[]


    for e in events:


        length = (
            e["end"]
            -
            e["start"]
        )


        # 太短刪掉

        if length < 30:

            continue



        # quantize

        e["start"] = quantize_tick(
            e["start"]
        )

        e["end"] = quantize_tick(
            e["end"]
        )


        if e["end"] <= e["start"]:

            e["end"] = (
                e["start"]
                +
                GRID
            )


        cleaned.append(e)



    # -----------------------
    # 單旋律化
    # -----------------------

    cleaned.sort(
        key=lambda x:x["start"]
    )


    melody=[]


    last_end=0


    for e in cleaned:


        # 去除重疊

        if e["start"] < last_end:


            if e["note"] != melody[-1]["note"]:

                continue



        melody.append(e)


        last_end=e["end"]



    print(
        "clean notes:",
        len(melody)
    )



    # -----------------------
    # 建立 MIDI
    # -----------------------

    out = MidiFile(
        ticks_per_beat=ticks
    )


    track = MidiTrack()


    out.tracks.append(
        track
    )



    current=0


    for e in melody:


        start=e["start"]

        end=e["end"]



        track.append(
            Message(
                "note_on",
                note=e["note"],
                velocity=e["velocity"],
                time=start-current
            )
        )


        track.append(
            Message(
                "note_off",
                note=e["note"],
                velocity=0,
                time=end-start
            )
        )


        current=end



    out.save(
        output_file
    )


    print(
        "DONE:"
    )

    print(
        output_file
    )



if __name__=="__main__":


    if len(sys.argv)<3:

        print(
            "python midi_cleaner.py input.mid output.mid"
        )

        sys.exit()



    clean_midi(
        sys.argv[1],
        sys.argv[2]
    )