import sys
import music21
from music21 import (
    converter,
    stream,
    note,
    meter,
    instrument
)


print("==============================")
print("CLEAN MUSICXML V28")
print("REBUILD SINGLE VOICE JIANPU")
print("==============================")


# -----------------------------
# 可接受節奏
# -----------------------------

DURATIONS = [
    4,
    2,
    1,
    0.5,
    0.25
]


def quantize(q):

    return min(
        DURATIONS,
        key=lambda x: abs(x-q)
    )



# -----------------------------
# 取得單旋律
# -----------------------------

def extract_melody(score):

    print("extract melody")


    src = score.parts[0]


    notes = []


    for n in src.recurse().notes:


        if isinstance(
            n,
            note.Note
        ):

            notes.append(
                n
            )


        elif n.isRest:

            notes.append(
                n
            )


    print(
        "notes:",
        len(notes)
    )


    return notes



# -----------------------------
# 建立新的4/4樂譜
# -----------------------------

def rebuild(notes):


    print(
        "rebuild score"
    )


    score = stream.Score()


    part = stream.Part()


    part.insert(
        0,
        instrument.Piano()
    )


    part.insert(
        0,
        meter.TimeSignature("4/4")
    )



    measure_no = 1

    m = stream.Measure(
        number=measure_no
    )


    current = 0



    for old in notes:


        q = float(
            old.duration.quarterLength
        )


        q = quantize(q)



        # 太長直接拆

        while current + q > 4:


            remain = 4-current


            if remain > 0:


                new = old.clone()

                new.duration.quarterLength = remain

                m.append(
                    new
                )


            part.append(
                m
            )


            measure_no += 1


            m = stream.Measure(
                number=measure_no
            )


            current = 0


            q -= remain



        new = old.clone()


        new.duration.quarterLength = q


        # 清除所有notation

        new.tie = None


        m.append(
            new
        )


        current += q



        if abs(current-4)<0.001:


            part.append(
                m
            )


            measure_no += 1


            m = stream.Measure(
                number=measure_no
            )


            current = 0



    # 最後補滿

    if len(m.notesAndRests)>0:


        diff = 4-current


        if diff > 0:


            r = note.Rest()

            r.duration.quarterLength = diff

            m.append(r)


        part.append(m)



    score.append(
        part
    )


    return score



# -----------------------------
# 最終檢查
# -----------------------------

def check(score):


    print(
        "FINAL CHECK"
    )


    for m in score.parts[0].getElementsByClass(
        stream.Measure
    ):


        total = sum(
            float(
                n.duration.quarterLength
            )
            for n in m.notesAndRests
        )


        print(
            "Measure",
            m.number,
            total
        )


        if abs(total-4)>0.01:

            print(
                "WARNING",
                m.number
            )



# -----------------------------
# main
# -----------------------------


def main():


    if len(sys.argv)<3:

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        return



    infile=sys.argv[1]

    outfile=sys.argv[2]


    print(
        "READ"
    )


    src = converter.parse(
        infile
    )


    notes = extract_melody(
        src
    )


    new_score = rebuild(
        notes
    )


    check(
        new_score
    )


    print(
        "WRITE"
    )


    new_score.write(
        "musicxml",
        fp=outfile
    )


    print(
        "DONE:"
    )

    print(
        outfile
    )



if __name__=="__main__":

    main()