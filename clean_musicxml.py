import sys
from music21 import converter, stream, note, chord, meter, duration
from fractions import Fraction

print("==============================")
print("CLEAN MUSICXML V31")
print("PUBLISH SCORE MODE")
print("JIANPU_LY COMPATIBLE")
print("==============================")


GRID = Fraction(1, 16)
BAR = Fraction(4, 1)


def quantize(x):
    """
    1/16 quantize
    """
    return float(round(Fraction(x) / GRID) * GRID)


def clean_duration(d):

    q = quantize(d)

    # 防止超短與非法 duration
    if q < 0.125:
        q = 0.125

    return q


def split_note(n, remain):

    """
    拆跨小節音符
    """

    result = []

    length = Fraction(clean_duration(n.duration.quarterLength))

    while length > remain:

        part = remain

        nn = note.Note(
            n.pitch,
            quarterLength=float(part)
        )

        result.append(nn)

        length -= part
        remain = BAR


    if length > 0:

        nn = note.Note(
            n.pitch,
            quarterLength=float(length)
        )

        result.append(nn)


    return result



def process_part(part):

    new_part = stream.Part()

    current = Fraction(0)


    for element in part.flatten().notesAndRests:


        # chords 取最高音
        if isinstance(element, chord.Chord):

            n = note.Note(
                element.pitches[-1],
                quarterLength=element.duration.quarterLength
            )

        elif isinstance(element, note.Note):

            n = element

        else:
            continue


        dur = Fraction(
            clean_duration(
                n.duration.quarterLength
            )
        )


        # 跨小節拆開

        remain = BAR - (current % BAR)


        pieces = split_note(
            n,
            remain
        )


        for p in pieces:

            new_part.append(p)

            current += Fraction(
                p.duration.quarterLength
            )


            # 小節結束
            if current % BAR == 0:

                pass


    return new_part



def rebuild_measure(score):

    out = stream.Score()


    for p in score.parts:

        np = process_part(p)

        np.insert(
            0,
            meter.TimeSignature("4/4")
        )

        out.append(np)


    return out



def main():

    if len(sys.argv) < 3:

        print(
            "usage: python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit(1)


    infile = sys.argv[1]

    outfile = sys.argv[2]


    print("read")

    score = converter.parse(infile)


    print("remove voices")
    print("remove chords")
    print("remove beams")
    print("remove ties")
    print("remove tuplets")


    clean = rebuild_measure(score)



    print("FINAL CHECK")


    for i,m in enumerate(
        clean.parts[0].measure(1,999).getElementsByClass('Measure'),
        1
    ):

        print(
            "Measure",
            i,
            float(m.duration.quarterLength)
        )


    print("FINAL WRITE")


    clean.write(
        "musicxml",
        fp=outfile
    )


    print("DONE")
    print(outfile)



if __name__ == "__main__":
    main()