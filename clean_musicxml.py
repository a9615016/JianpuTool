# ==========================================================
# CLEAN MUSICXML V63.1
# Absolute Quantize Engine Fix
# BasicPitch + Render + jianpu_ly
# ==========================================================

import sys
from music21 import converter, stream, note, chord, meter, duration


STEP = 0.25


def quantize(x):
    return round(x / STEP) * STEP



def collect_notes(src):

    result=[]

    for n in src.recurse():

        if isinstance(n, note.Note):

            q=max(
                STEP,
                quantize(
                    n.duration.quarterLength
                )
            )

            nn=note.Note(
                n.pitch
            )

            nn.duration=duration.Duration(q)

            result.append(nn)


        elif isinstance(n, chord.Chord):

            if len(n.pitches):

                q=max(
                    STEP,
                    quantize(
                        n.duration.quarterLength
                    )
                )

                nn=note.Note(
                    n.pitches[-1]
                )

                nn.duration=duration.Duration(q)

                result.append(nn)


    return result



def rebuild_score(notes):

    score=stream.Score()

    part=stream.Part()

    part.insert(
        0,
        meter.TimeSignature("4/4")
    )


    measure_no=1

    current=0

    m=stream.Measure(
        number=measure_no
    )


    for n in notes:


        q=quantize(
            n.duration.quarterLength
        )


        # 超過小節

        if current+q > 4.0:


            rest=quantize(
                4.0-current
            )

            if rest>0:

                m.insert(
                    current,
                    note.Rest(
                        quarterLength=rest
                    )
                )


            part.append(m)


            measure_no+=1

            m=stream.Measure(
                number=measure_no
            )

            current=0



        # 強制 offset

        m.insert(
            current,
            n
        )


        current+=q



        if abs(current-4.0)<0.001:


            part.append(m)

            measure_no+=1

            m=stream.Measure(
                number=measure_no
            )

            current=0



    if current>0:

        rest=quantize(
            4.0-current
        )

        if rest>0:

            m.insert(
                current,
                note.Rest(
                    quarterLength=rest
                )
            )

        part.append(m)



    score.append(part)


    # ★關鍵修正

    print(
        "FORCE MAKE MEASURES"
    )


    score = (
        score
        .flatten()
        .makeMeasures()
    )


    score.makeNotation(
        inPlace=True
    )


    return score



def verify(score):

    print(
        "FINAL CHECK"
    )

    bad=False


    for m in score.parts[0].getElementsByClass(
        "Measure"
    ):

        q=m.duration.quarterLength


        print(
            "Measure",
            m.number,
            q
        )


        if abs(q-4.0)>0.001:

            bad=True



    if bad:

        print(
            "WARNING measure mismatch"
        )

    else:

        print(
            "ALL MEASURES SAFE"
        )



def main():

    if len(sys.argv)<3:

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        return


    inp=sys.argv[1]

    out=sys.argv[2]


    print("================")
    print(
        "CLEAN MUSICXML V63.1"
    )
    print(
        "Absolute Quantize Engine Fix"
    )
    print("================")


    print("read")

    src=converter.parse(inp)


    print("remove voices")
    print("remove chords")
    print("remove beams")
    print("remove ties")


    print(
        "collect melody"
    )


    notes=collect_notes(src)


    print(
        "notes:",
        len(notes)
    )


    print(
        "quantize offset + duration"
    )


    score=rebuild_score(notes)


    verify(score)


    print(
        "FINAL WRITE"
    )


    score.write(
        "musicxml",
        fp=out
    )


    print(
        "DONE"
    )

    print(out)



if __name__=="__main__":
    main()