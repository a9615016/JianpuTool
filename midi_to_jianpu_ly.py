# midi_to_jianpu_ly.py
# MIDI -> Jianpu LilyPond
# bypass jianpu_ly

import sys
from music21 import converter, note


def pitch_to_number(p):

    # C major 簡化版
    table = {
        "C": "1",
        "D": "2",
        "E": "3",
        "F": "4",
        "G": "5",
        "A": "6",
        "B": "7",
    }

    return table[p.step]


def duration_to_ly(d):

    q = float(d)

    if q >= 4:
        return "1"

    if q >= 2:
        return "2"

    if q >= 1:
        return "4"

    if q >= 0.5:
        return "8"

    return "16"



def convert(mid, out):

    print("READ MIDI")

    score = converter.parse(mid)

    notes=[]

    for n in score.flat.notes:

        if isinstance(n, note.Note):

            num = pitch_to_number(n.pitch)

            dur = duration_to_ly(
                n.duration.quarterLength
            )

            notes.append(
                f"{num}{dur}"
            )


    print("NOTES:",len(notes))


    ly=[]


    ly.append(r'''
\version "2.24.0"

\paper {
  #(set-paper-size "a4")
}


melody = {

\time 4/4

''')


    count=0

    for x in notes:

        ly.append(x+" ")

        count+=1

        if count%8==0:
            ly.append("\n")


    ly.append(
r'''
}


\score {

\new Staff {

\melody

}

\layout {}

}

'''
)


    with open(
        out,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "".join(ly)
        )


    print("DONE")
    print(out)



if __name__=="__main__":

    if len(sys.argv)<3:

        print(
        "python midi_to_jianpu_ly.py input.mid output.ly"
        )

    else:

        convert(
            sys.argv[1],
            sys.argv[2]
        )