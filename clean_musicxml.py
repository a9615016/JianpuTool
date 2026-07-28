# clean_musicxml.py
# CLEAN MUSICXML V81 FINAL
# Absolute Beat Grid Engine
# Jianpu_ly Compatible

import sys
from music21 import converter, stream, note, meter, duration, clef, chord


VERSION = "CLEAN MUSICXML V81 FINAL ABSOLUTE GRID ENGINE"


TARGET_BEATS = 4
DIVISIONS = 4   # quarter note = 1 beat


def quantize_length(q):

    allowed = [
        4.0,
        2.0,
        1.0,
        0.5,
        0.25
    ]

    best = min(
        allowed,
        key=lambda x: abs(x-q)
    )

    return best



def split_notes(notes):

    result = []

    current = 0

    for n in notes:

        dur = quantize_length(
            n.duration.quarterLength
        )


        while dur > 0:

            remain = TARGET_BEATS - current

            take = min(
                dur,
                remain
            )


            if isinstance(n, note.Note):

                nn = note.Note(
                    n.pitch
                )

            else:
                nn = note.Rest()


            nn.duration = duration.Duration(
                take
            )


            result.append(nn)

            current += take
            dur -= take


            if current >= TARGET_BEATS:

                result.append("BAR")
                current = 0


    if current > 0:

        result.append(
            note.Rest(
                quarterLength=TARGET_BEATS-current
            )
        )

        result.append("BAR")


    return result



def rebuild_part(part):

    new_part = stream.Part()

    new_part.insert(
        0,
        meter.TimeSignature("4/4")
    )


    notes=[]


    for n in part.recurse():

        if isinstance(n, note.Note):

            notes.append(n)


        elif isinstance(n, chord.Chord):

            # 只留最高音旋律
            nn = note.Note(
                n.sortAscending().notes[-1].pitch
            )

            nn.duration = n.duration

            notes.append(nn)



    rebuilt = split_notes(notes)


    m = stream.Measure(
        number=1
    )

    beat=0
    measure_no=1


    for item in rebuilt:


        if item=="BAR":

            new_part.append(m)

            measure_no +=1

            m = stream.Measure(
                number=measure_no
            )

            beat=0

            continue


        m.append(item)

        beat += item.duration.quarterLength



    return new_part



def check(score):

    print("FINAL CHECK")

    ok=True

    for i,m in enumerate(
        score.parts[0].getElementsByClass("Measure"),
        1
    ):

        total=sum(
            x.duration.quarterLength
            for x in m.notesAndRests
        )

        print(
            "Measure",
            i,
            total
        )

        if abs(total-4)>0.001:

            ok=False


    if ok:

        print(
            "ALL MEASURES SAFE"
        )

    else:

        print(
            "MEASURE ERROR"
        )


    return ok



def main():

    print("================")
    print(VERSION)
    print("================")


    infile=sys.argv[1]


    outfile = (
        sys.argv[2]
        if len(sys.argv)>2
        else "clean.musicxml"
    )


    print("read")

    score=converter.parse(
        infile
    )


    print("remove voices")
    print("remove chords")
    print("remove beams")
    print("remove ties")


    new_score=stream.Score()


    for p in score.parts:

        new_score.append(
            rebuild_part(p)
        )


    print("clear notation cache")


    check(
        new_score
    )


    print("FINAL WRITE")


    new_score.write(
        "musicxml",
        fp=outfile
    )


    print("DONE")
    print(outfile)



if __name__=="__main__":
    main()