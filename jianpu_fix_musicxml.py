# jianpu_fix_musicxml.py
# V6.0
# Jianpu_ly timing repair

import sys
from music21 import converter, stream, note, chord, meter, clef


GRID = [
    4.0,    # quarter
    2.0,    # half
    1.0,    # eighth
    0.5     # 16th
]


def quantize_duration(q):

    best = min(
        GRID,
        key=lambda x: abs(x-q)
    )

    return best



def rebuild_score(src):

    print("================")
    print("JIANPU FIX MUSICXML V6.0")
    print("================")


    score = converter.parse(src)


    out = stream.Score()


    for part in score.parts:

        print("processing part")


        new_part = stream.Part()


        # force 4/4
        new_part.append(
            meter.TimeSignature("4/4")
        )


        new_part.append(
            clef.TrebleClef()
        )


        current_measure = stream.Measure(
            number=1
        )


        beat_used = 0



        for element in part.flatten().notesAndRests:


            # skip chord
            if isinstance(element, chord.Chord):

                n = note.Note(
                    element.root()
                )

            else:

                n = element



            dur = float(
                n.duration.quarterLength
            )


            # remove abnormal duration

            if dur <= 0:
                continue


            dur = quantize_duration(dur)


            # split measure

            if beat_used + dur > 4:

                while beat_used < 4:

                    r = note.Rest(
                        quarterLength=
                        4-beat_used
                    )

                    current_measure.append(r)

                    beat_used += r.duration.quarterLength



                new_part.append(
                    current_measure
                )


                current_measure = stream.Measure(
                    number=current_measure.number+1
                )

                beat_used = 0



            nn = note.Rest() if n.isRest else note.Note(n.pitch)


            nn.duration.quarterLength = dur


            current_measure.append(nn)


            beat_used += dur



        # fill last measure

        if beat_used < 4:

            r = note.Rest(
                quarterLength=4-beat_used
            )

            current_measure.append(r)


        new_part.append(
            current_measure
        )


        out.append(new_part)



    return out




def main():

    if len(sys.argv)<3:

        print(
            "usage:"
            " python jianpu_fix_musicxml.py input.musicxml output.musicxml"
        )

        return


    src=sys.argv[1]
    dst=sys.argv[2]


    fixed = rebuild_score(src)


    print("FINAL CHECK")


    for p in fixed.parts:

        for m in p.getElementsByClass("Measure"):

            total=sum(
                x.duration.quarterLength
                for x in m.flatten().notesAndRests
            )

            print(
                "Measure",
                m.number,
                total
            )



    fixed.write(
        "musicxml",
        dst
    )


    print("DONE")
    print(dst)



if __name__=="__main__":
    main()