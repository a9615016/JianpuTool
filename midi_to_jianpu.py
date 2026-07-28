from music21 import converter, note, stream
import sys


VERSION = "######## V85 PURE JIANPU MIDI ENGINE ########"


# quarterLength → LilyPond
def duration_to_ly(d):

    table = {
        4.0: "1",
        2.0: "2",
        1.0: "4",
        0.5: "8",
        0.25: "16",
        0.125: "32"
    }

    nearest = min(
        table.keys(),
        key=lambda x: abs(x-d)
    )

    return table[nearest]


# MIDI pitch → 簡譜
def pitch_to_number(p):

    names = {
        0:"1",
        1:"#1",
        2:"2",
        3:"#2",
        4:"3",
        5:"4",
        6:"#4",
        7:"5",
        8:"#5",
        9:"6",
        10:"#6",
        11:"7"
    }

    octave = p // 12

    return names[p % 12], octave



def convert(mid,out):

    print(VERSION)

    midi = converter.parse(mid)


    notes=[]


    for n in midi.recurse().notes:

        if isinstance(n,note.Note):

            notes.append(n)



    print(
        "notes:",
        len(notes)
    )


    ly=[]


    ly.append(
"""
\\version "2.24.0"

\\header {
 title = "Jianpu V85"
}

melody = {

\\time 4/4

"""
    )


    beat=0


    for n in notes:


        num,octave=pitch_to_number(
            n.pitch.midi
        )


        dur=duration_to_ly(
            float(n.duration.quarterLength)
        )


        ly.append(
            num+dur+" "
        )


        beat += float(
            n.duration.quarterLength
        )


        # 自動小節
        if beat >=4:

            ly.append("| ")

            beat=0



    ly.append(
"""
}

\\score {
 <<
  \\new Staff {
   \\melody
  }
 >>
}
"""
    )


    with open(
        out,
        "w",
        encoding="utf8"
    ) as f:

        f.write(
            "".join(ly)
        )


    print(
        "DONE",
        out
    )



if __name__=="__main__":


    convert(
        sys.argv[1],
        sys.argv[2]
    )