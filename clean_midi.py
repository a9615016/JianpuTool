#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CLEAN MIDI V1
For:
BasicPitch MIDI -> MusicXML -> Jianpu

功能:
- remove overlap notes
- remove tiny notes
- quantize timing
- rebuild melody track
"""

import sys
import mido
from mido import MidiFile, MidiTrack, Message


MIN_NOTE_LENGTH = 30     # ticks
GRID = 120               # quantize ticks


def quantize(value):
    return int(round(value / GRID) * GRID)


def clean_midi(input_file, output_file):

    print("================")
    print("CLEAN MIDI V1")
    print("================")

    print("read midi")

    mid = MidiFile(input_file)

    ticks = mid.ticks_per_beat

    print("ticks:", ticks)


    notes = []

    current = {}

    time = 0


    print("collect notes")


    for track in mid.tracks:

        time = 0

        for msg in track:

            time += msg.time


            if msg.type == "note_on" and msg.velocity > 0:

                current[msg.note] = {
                    "start": time,
                    "velocity": msg.velocity
                }


            elif msg.type in ["note_off","note_on"]:

                if msg.note in current:

                    n = current[msg.note]

                    end = time

                    if end > n["start"]:

                        notes.append({
                            "pitch": msg.note,
                            "start": n["start"],
                            "end": end,
                            "velocity": n["velocity"]
                        })

                    del current[msg.note]


    print("notes:", len(notes))


    print("remove tiny notes")


    cleaned=[]

    for n in notes:

        length=n["end"]-n["start"]

        if length >= MIN_NOTE_LENGTH:
            cleaned.append(n)


    print("after tiny remove:",len(cleaned))


    print("quantize")


    for n in cleaned:

        n["start"]=quantize(n["start"])
        n["end"]=quantize(n["end"])

        if n["end"] <= n["start"]:
            n["end"]=n["start"]+GRID



    print("remove overlap")


    cleaned.sort(
        key=lambda x:(x["start"],x["pitch"])
    )


    final=[]

    last_end={}


    for n in cleaned:

        pitch=n["pitch"]

        if pitch in last_end:

            if n["start"] < last_end[pitch]:

                n["start"]=last_end[pitch]


        if n["end"]>n["start"]:

            final.append(n)
            last_end[pitch]=n["end"]



    print("final notes:",len(final))


    print("write midi")


    out=MidiFile(
        ticks_per_beat=ticks
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



if __name__=="__main__":

    if len(sys.argv)<3:

        print(
            "usage: python clean_midi.py input.mid output.mid"
        )

        sys.exit()


    clean_midi(
        sys.argv[1],
        sys.argv[2]
    )