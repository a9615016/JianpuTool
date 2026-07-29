import sys
from music21 import converter, stream, note, chord, meter
from fractions import Fraction


print("==============================")
print("CLEAN MUSICXML V32")
print("MEASURE REBUILDER")
print("JIANPU_LY COMPATIBLE")
print("==============================")


GRID = Fraction(1,16)
BAR = Fraction(4,1)


def quantize(v):
    return round(Fraction(v) / GRID) * GRID


def normalize_duration(v):

    q = quantize(v)

    if q <= 0:
        q = Fraction(1,16)

    return q



def extract_notes(score):

    notes=[]

    for n in score.recurse().notes:

        if isinstance(n, chord.Chord):

            n = note.Note(
                n.pitches[-1]
            )

        n.duration.quarterLength = float(
            normalize_duration(
                n.duration.quarterLength
            )
        )

        notes.append(n)

    return notes



def rebuild_measures(notes):

    result = stream.Part()

    result.insert(
        0,
        meter.TimeSignature("4/4")
    )


    current_measure = stream.Measure()

    beat = Fraction(0)


    measure_no = 1


    for n in notes:

        dur = Fraction(
            n.duration.quarterLength
        )


        # 跨小節拆開

        while beat + dur > BAR:


            remain = BAR - beat


            if remain > 0:

                part = note.Note(
                    n.pitch,
                    quarterLength=float(remain)
                )

                current_measure.append(part)


            result.append(
                current_measure
            )


            print(
                "Measure",
                measure_no,
                4.0
            )

            measure_no += 1


            current_measure = stream.Measure()


            dur -= remain

            beat = Fraction(0)



        if dur > 0:

            part = note.Note(
                n.pitch,
                quarterLength=float(dur)
            )

            current_measure.append(part)

            beat += dur



        if beat == BAR:

            result.append(
                current_measure
            )

            print(
                "Measure",
                measure_no,
                4.0
            )

            measure_no += 1

            current_measure = stream.Measure()

            beat = Fraction(0)



    # 最後補滿

    if beat > 0:

        rest = note.Rest(
            quarterLength=float(
                BAR-beat
            )
        )

        current_measure.append(rest)

        result.append(
            current_measure
        )

        print(
            "Measure",
            measure_no,
            4.0
        )


    return result



def main():

    if len(sys.argv)<3:

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        return


    src=sys.argv[1]
    dst=sys.argv[2]


    print("read")

    score=converter.parse(src)


    print("remove voices")
    print("remove chords")
    print("remove beams")
    print("remove ties")


    notes=extract_notes(score)


    print(
        "notes:",
        len(notes)
    )


    new_score=stream.Score()


    part=rebuild_measures(notes)


    new_score.append(part)


    print("FINAL CHECK")


    for m in part.getElementsByClass(
        stream.Measure
    ):

        print(
            "Measure",
            m.number,
            float(m.duration.quarterLength)
        )


    print("FINAL WRITE")


    new_score.write(
        "musicxml",
        fp=dst
    )


    print("DONE")
    print(dst)



if __name__=="__main__":
    main()