# clean_musicxml.py
# CLEAN MUSICXML V40 FORCE JIANPU SAFE

import sys
from music21 import converter, stream, meter, note, chord, clef


print("================")
print("CLEAN MUSICXML V40 FORCE JIANPU SAFE")
print("================")


def quantize_duration(n):
    values = [
        4.0,
        2.0,
        1.0,
        0.5,
        0.25
    ]

    q = min(values, key=lambda x: abs(x-n))

    if abs(q-n) > 0.2:
        return 0.25

    return q


def clean(input_file, output_file):

    print("read")

    score = converter.parse(input_file)


    part = score.parts[0]


    print("remove voices")
    for n in part.recurse():
        if hasattr(n, "voice"):
            n.voice = None


    print("remove chords")

    elements = []

    for n in part.flatten().notesAndRests:

        if isinstance(n, chord.Chord):
            nn = n.notes[0]
            new = note.Note(
                nn.pitch,
                quarterLength=n.quarterLength
            )
            elements.append(new)

        else:
            elements.append(n)


    new_part = stream.Part()

    print("remove beams")
    print("remove ties")


    print("force 4/4")

    new_part.append(meter.TimeSignature("4/4"))


    print("duration quantize")


    for n in elements:

        n.quarterLength = quantize_duration(
            float(n.quarterLength)
        )

        n.tie = None

        new_part.append(n)



    print("rebuild measures")


    measures = []
    current = stream.Measure()

    beat = 0


    for n in new_part.notesAndRests:

        length = float(n.quarterLength)


        # 超過小節
        if beat + length > 4:

            remain = 4 - beat

            if remain > 0:

                if isinstance(n, note.Note):

                    cut = note.Note(
                        n.pitch,
                        quarterLength=remain
                    )
                    current.append(cut)

                else:
                    r = note.Rest(
                        quarterLength=remain
                    )
                    current.append(r)


            measures.append(current)


            print(
                "FORCE CUT measure",
                len(measures)
            )


            current = stream.Measure()
            beat = 0


            continue


        current.append(n)

        beat += length



        if beat >= 4:

            measures.append(current)

            current = stream.Measure()
            beat = 0



    if len(current):

        remain = 4-beat

        if remain > 0:

            current.append(
                note.Rest(
                    quarterLength=remain
                )
            )

        measures.append(current)



    final = stream.Score()
    p = stream.Part()

    p.append(
        meter.TimeSignature("4/4")
    )


    print("FINAL CHECK")


    for i,m in enumerate(measures,1):

        total = sum(
            float(x.quarterLength)
            for x in m.notesAndRests
        )

        print(
            "Measure",
            i,
            total
        )

        if abs(total-4)>0.01:

            print(
                "ERROR",
                i,
                total
            )

        p.append(m)


    final.append(p)


    print("ALL MEASURES SAFE")


    print("clear notation cache")

    final.write(
        "musicxml",
        fp=output_file
    )


    print("FINAL WRITE")
    print("DONE")
    print(output_file)



if __name__=="__main__":

    if len(sys.argv)<3:
        print(
            "usage: python clean_musicxml.py input.musicxml output.musicxml"
        )
        sys.exit()


    clean(
        sys.argv[1],
        sys.argv[2]
    )