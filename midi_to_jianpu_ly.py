from music21 import converter, stream, note, meter, tempo
import sys


VERSION = "MIDI DIRECT TO JIANPU LY V1"


# 4/4
BEATS_PER_BAR = 4



def duration_to_ly(d):

    """
    music21 duration
    轉 LilyPond duration
    """

    q = float(d)


    table = {
        4.0: "1",
        2.0: "2",
        1.0: "4",
        0.5: "8",
        0.25: "16"
    }


    if q in table:
        return table[q]


    # fallback
    return "4"





def pitch_to_number(n):

    """
    MIDI pitch
    轉簡譜數字
    C=1 D=2...
    """

    mapping = {
        "C": "1",
        "D": "2",
        "E": "3",
        "F": "4",
        "G": "5",
        "A": "6",
        "B": "7"
    }


    return mapping[
        n.pitch.step
    ]





def midi_to_jianpu(inp, out):


    print(VERSION)


    score = converter.parse(inp)


    notes = []


    # 第一軌旋律

    for n in score.recurse().notesAndRests:


        if n.isRest:

            notes.append(
                "0" +
                duration_to_ly(
                    n.duration.quarterLength
                )
            )


        else:

            num = pitch_to_number(n)


            notes.append(
                num +
                duration_to_ly(
                    n.duration.quarterLength
                )
            )



    ly = []


    ly.append(
        '\\version "2.24.0"'
    )


    ly.append(
        '\\paper { }'
    )


    ly.append(
        '\\score {'
    )


    ly.append(
        '  \\new Staff {'
    )


    ly.append(
        '    \\numericTimeSignature'
    )


    ly.append(
        '    \\time 4/4'
    )


    ly.append(
        '    \\relative c {'
    )


    # 寫入音符

    ly.append(
        " ".join(notes)
    )


    ly.append(
        '    }'
    )


    ly.append(
        '  }'
    )


    ly.append(
        '}'
    )



    with open(
        out,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "\n".join(ly)
        )



    print("DONE")

    print(out)





if __name__ == "__main__":


    if len(sys.argv)<3:

        print(
            "python midi_to_jianpu_ly.py input.mid output.ly"
        )

        exit()


    midi_to_jianpu(
        sys.argv[1],
        sys.argv[2]
    )