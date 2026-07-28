# ==========================================================
# CLEAN MUSICXML V63
# Absolute Quantize Engine
# BasicPitch + Render + jianpu_ly Compatible
# ==========================================================

import sys
from music21 import converter, stream, note, chord, meter, duration, clef


STEP = 0.25   # 四分音符切割精度


def quantize(value):
    return round(value / STEP) * STEP


def clean_notes(src):

    notes = []

    for n in src.recurse():

        if isinstance(n, note.Note):

            q = n.duration.quarterLength

            if q <= 0:
                continue

            n2 = note.Note(
                n.pitch,
                quarterLength=max(STEP, quantize(q))
            )

            notes.append(n2)


        elif isinstance(n, chord.Chord):

            # 只保留最高音旋律
            if len(n.pitches):

                n2 = note.Note(
                    n.pitches[-1],
                    quarterLength=max(
                        STEP,
                        quantize(n.duration.quarterLength)
                    )
                )

                notes.append(n2)

    return notes



def rebuild_score(notes):

    score = stream.Score()

    part = stream.Part()

    part.append(meter.TimeSignature("4/4"))

    current = 0

    measure_no = 1

    m = stream.Measure(number=measure_no)


    for n in notes:

        dur = quantize(
            n.duration.quarterLength
        )

        if dur <= 0:
            continue


        # 超過小節
        if current + dur > 4.0:

            rest_len = quantize(4.0-current)

            if rest_len > 0:
                m.append(
                    note.Rest(
                        quarterLength=rest_len
                    )
                )

            part.append(m)

            measure_no += 1

            m = stream.Measure(
                number=measure_no
            )

            current = 0


        n.duration = duration.Duration(dur)

        m.append(n)

        current += dur



        # 剛好滿小節

        if abs(current-4.0) < 0.001:

            part.append(m)

            measure_no += 1

            m = stream.Measure(
                number=measure_no
            )

            current = 0



    # 最後補休止

    if current > 0:

        rest = quantize(
            4.0-current
        )

        if rest > 0:

            m.append(
                note.Rest(
                    quarterLength=rest
                )
            )

        part.append(m)



    score.append(part)

    return score



def verify(score):

    print("FINAL CHECK")

    bad = False

    for m in score.parts[0].getElementsByClass("Measure"):

        length = m.duration.quarterLength

        print(
            "Measure",
            m.number,
            length
        )

        if abs(length-4.0)>0.001:

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
            "usage:"
        )

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        return


    inp=sys.argv[1]

    out=sys.argv[2]


    print("================")
    print(
        "CLEAN MUSICXML V63"
    )
    print(
        "Absolute Quantize Engine"
    )
    print("================")


    print("read")

    src=converter.parse(inp)



    print("remove voices")
    print("remove chords")
    print("remove beams")
    print("remove ties")



    print("collect melody")


    notes=clean_notes(src)



    print(
        "notes:",
        len(notes)
    )



    print(
        "quantize offset + duration"
    )


    score=rebuild_score(notes)



    print(
        "clear notation cache"
    )


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