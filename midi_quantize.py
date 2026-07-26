from mido import MidiFile, MidiTrack, Message
import sys
import os


VERSION = "MIDI QUANTIZE V1"


# 16分音符量化
GRID = 120 / 4


def quantize_tick(tick):
    return int(round(tick / GRID) * GRID)



def clean_midi(input_file, output_file):

    print(VERSION)
    print("input:", input_file)


    mid = MidiFile(input_file)


    new_mid = MidiFile(
        ticks_per_beat=mid.ticks_per_beat
    )


    for track in mid.tracks:

        new_track = MidiTrack()

        abs_time = 0


        events=[]


        for msg in track:

            abs_time += msg.time


            if msg.type in [
                "note_on",
                "note_off"
            ]:

                events.append(
                    (
                        abs_time,
                        msg
                    )
                )


        for tick,msg in events:

            new_tick = quantize_tick(tick)


            new_track.append(
                msg.copy(
                    time=new_tick
                )
            )


        new_mid.tracks.append(
            new_track
        )



    new_mid.save(output_file)


    print("done:")
    print(output_file)



if __name__=="__main__":


    if len(sys.argv)<2:

        print(
            "python midi_quantize.py input.mid output.mid"
        )

        exit()


    inp=sys.argv[1]


    if len(sys.argv)>=3:

        out=sys.argv[2]

    else:

        out=os.path.splitext(inp)[0]+"_clean.mid"



    clean_midi(inp,out)