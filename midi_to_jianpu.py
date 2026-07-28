# midi_to_jianpu.py
# VERSION: V85 PURE MIDI JIANPU CONVERTER

from music21 import converter, note, chord, stream
import sys


VERSION = "V85 PURE MIDI JIANPU"


# -------------------------
# duration quantize
# -------------------------

def quantize(q):

    table = [
        (4,"----"),
        (2,"--"),
        (1,""),
        (0.5,"_"),
        (0.25,"__"),
    ]

    return min(
        table,
        key=lambda x:abs(x[0]-q)
    )



# -------------------------
# MIDI note -> number
# -------------------------

def midi_to_number(pitch):

    # C major
    scale = {
        0:"1",
        2:"2",
        4:"3",
        5:"4",
        7:"5",
        9:"6",
        11:"7"
    }

    pc = pitch.pitchClass

    return scale.get(pc,"0")



# -------------------------
# extract melody
# -------------------------

def extract_melody(score):

    notes=[]


    for n in score.recurse():

        if isinstance(n,note.Note):

            notes.append(n)


        elif isinstance(n,chord.Chord):

            # take highest note
            notes.append(
                n.sortAscending()[-1]
            )


    return notes




# -------------------------
# build jianpu
# -------------------------

def build_jianpu(notes):

    result=[]

    beat=0


    for n in notes:

        num=midi_to_number(n)


        q=float(
            n.duration.quarterLength
        )


        length,mark=quantize(q)


        result.append(
            num+mark
        )


        beat+=length


        # force 4/4
        if beat>=4:

            result.append("|")

            beat=0



    return " ".join(result)




# -------------------------
# main
# -------------------------

def convert(inp,out):

    print(VERSION)

    score=converter.parse(inp)


    notes=extract_melody(score)


    print(
        "notes:",
        len(notes)
    )


    text=build_jianpu(notes)


    with open(
        out,
        "w",
        encoding="utf8"
    ) as f:

        f.write(text)


    print("DONE")
    print(out)



if __name__=="__main__":

    if len(sys.argv)<3:

        print(
        "python midi_to_jianpu.py input.mid output.txt"
        )

        exit()


    convert(
        sys.argv[1],
        sys.argv[2]
    )