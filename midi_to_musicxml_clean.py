from music21 import converter, stream, note, chord, meter
import sys


print("MIDI TO MUSICXML STRICT")


def convert(mid, out):

    score = converter.parse(mid)

    flat = score.flatten()


    part = stream.Part()


    part.insert(
        0,
        meter.TimeSignature("4/4")
    )


    print("EXTRACT NOTES")


    for n in flat.notes:


        if isinstance(n, chord.Chord):

            nn = note.Note(
                n.highest.pitch
            )

            nn.duration = n.duration


        else:

            nn = n


        # 強制16分音符網格

        q = nn.duration.quarterLength


        if q <= 0:
            continue


        if q < 0.25:
            q = 0.25


        q = round(q * 4) / 4


        nn.duration.quarterLength = q


        part.append(nn)



    print("MAKE MEASURES")


    measures = part.makeMeasures(
        inPlace=False
    )


    print("WRITE XML")


    measures.write(
        "musicxml",
        fp=out
    )


    print("DONE", out)



if __name__=="__main__":

    convert(
        sys.argv[1],
        sys.argv[2]
    )