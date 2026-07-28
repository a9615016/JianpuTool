#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
clean_midi.py V1

用途:
BasicPitch melody.mid
        ↓
clean.mid

功能:
1. 移除重疊音符
2. 移除過短音符
3. 節奏量化
4. 保留單旋律
5. 修正 note start/end

"""

import sys
from mido import MidiFile, MidiTrack, Message


MIN_LENGTH = 30      # 最短音符 ticks
GRID = 120           # quantize 格子



def quantize(t):

    return int(round(t / GRID) * GRID)



def clean_midi(input_file, output_file):

    print("================")
    print("CLEAN MIDI V1")
    print("================")


    mid = MidiFile(input_file)


    print("ticks:", mid.ticks_per_beat)


    notes = []


    active = {}


    print("collect notes")


    for track in mid.tracks:

        current_time = 0


        for msg in track:

            current_time += msg.time


            if msg.type == "note_on" and msg.velocity > 0:

                active[msg.note] = {
                    "start": current_time,
                    "velocity": msg.velocity
                }


            elif (
                msg.type == "note_off"
                or
                (
                    msg.type == "note_on"
                    and msg.velocity == 0
                )
            ):


                if msg.note in active:

                    n = active[msg.note]


                    length = current_time - n["start"]


                    if length > 0:

                        notes.append({

                            "pitch": msg.note,

                            "start": n["start"],

                            "end": current_time,

                            "velocity": n["velocity"]

                        })


                    del active[msg.note]



    print("notes:", len(notes))



    print("remove tiny notes")


    cleaned=[]


    for n in notes:

        if n["end"] - n["start"] >= MIN_LENGTH:

            cleaned.append(n)



    print(
        "after remove:",
        len(cleaned)
    )



    print("quantize")


    for n in cleaned:

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



    print("remove overlap")


    cleaned.sort(
        key=lambda x:
        (
            x["start"],
            x["pitch"]
        )
    )


    final=[]


    last_end={}



    for n in cleaned:


        pitch=n["pitch"]


        if pitch in last_end:


            if n["start"] < last_end[pitch]:

                n["start"] = last_end[pitch]



        if n["end"] > n["start"]:

            final.append(n)

            last_end[pitch]=n["end"]



    print(
        "final notes:",
        len(final)
    )



    print("write midi")


    out=MidiFile(
        ticks_per_beat=mid.ticks_per_beat
    )


    track=MidiTrack()


    out.tracks.append(track)



    events=[]


    for n in final:


        events.append(
            (
                n["start"],

                Message(
                    "note_on",
                    note=n["pitch"],
                    velocity=n["velocity"],
                    time=0
                )
            )
        )


        events.append(
            (
                n["end"],

                Message(
                    "note_off",
                    note=n["pitch"],
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


        msg.time=t-last

        track.append(msg)

        last=t



    out.save(output_file)



    print("================")
    print("DONE")
    print(output_file)
    print("================")




if __name__ == "__main__":


    if len(sys.argv) < 3:

        print(
            "usage:"
            " python clean_midi.py input.mid output.mid"
        )

        sys.exit(1)



    clean_midi(
        sys.argv[1],
        sys.argv[2]
    )