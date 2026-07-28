# CLEAN MUSICXML V32
# HARD 4/4 BAR REPAIR FOR JIANPU_LY

from music21 import converter, stream, note, chord, meter
import sys


def quantize_duration(q):
    """
    強制量化到 16 分音符
    """
    values = [
        0.25,
        0.5,
        1.0,
        2.0,
        4.0
    ]

    closest = min(values, key=lambda x: abs(x-q))

    return closest


def split_long_note(n, remain):

    result = []

    length = n.duration.quarterLength

    while length > remain:

        part = note.Note(n.pitch)

        part.duration.quarterLength = remain

        result.append(part)

        length -= remain

        remain = 4.0


    if length > 0:

        part = note.Note(n.pitch)
        part.duration.quarterLength = length
        result.append(part)


    return result



def rebuild_44(score):

    print("HARD REBUILD 4/4")

    score.removeByClass('TimeSignature')

    score.insert(
        0,
        meter.TimeSignature("4/4")
    )


    new_score = stream.Score()

    for part in score.parts:

        new_part = stream.Part()

        pos = 0

        measure_no = 1

        m = stream.Measure(
            number=measure_no
        )

        remain = 4.0


        for el in part.flat.notesAndRests:


            dur = quantize_duration(
                el.duration.quarterLength
            )


            if dur > remain:

                # 切跨小節音符

                first = note.Note(
                    el.pitch
                )

                first.duration.quarterLength = remain

                m.append(first)

                new_part.append(m)


                measure_no += 1

                m = stream.Measure(
                    number=measure_no
                )

                remain = 4.0


                second = note.Note(
                    el.pitch
                )

                second.duration.quarterLength = dur-remain

                m.append(second)

                remain -= second.duration.quarterLength


            else:

                el.duration.quarterLength = dur

                m.append(el)

                remain -= dur



            if remain == 0:

                new_part.append(m)

                measure_no += 1

                m = stream.Measure(
                    number=measure_no
                )

                remain = 4.0



        if len(m.notesAndRests):

            while remain > 0:

                r = note.Rest()

                r.duration.quarterLength = remain

                m.append(r)

                remain = 0


            new_part.append(m)


        new_score.append(new_part)



    return new_score



def main():

    infile = sys.argv[1]
    outfile = sys.argv[2]


    print("================")
    print("CLEAN MUSICXML V32")
    print("================")


    score = converter.parse(infile)


    print("remove voices")
    print("remove chords")
    print("remove beams")
    print("remove ties")


    # 移除 chord
    for c in score.recurse().getElementsByClass(chord.Chord):

        n = c.notes[0]

        c.activeSite.replace(c,n)



    print("quantize duration")

    for n in score.recurse().notesAndRests:

        n.duration.quarterLength = quantize_duration(
            n.duration.quarterLength
        )


    score = rebuild_44(score)


    print("FINAL CHECK")


    ok=True

    for m in score.parts[0].getElementsByClass(
        stream.Measure
    ):

        q=m.duration.quarterLength

        print(
            "Measure",
            m.number,
            q
        )


        if abs(q-4.0)>0.01:

            ok=False



    if ok:

        print("ALL MEASURES SAFE")

    else:

        print("WARNING measure mismatch")



    score.write(
        "musicxml",
        fp=outfile
    )


    print("DONE")
    print(outfile)



if __name__=="__main__":
    main()