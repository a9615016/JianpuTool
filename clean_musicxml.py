import sys
import music21
import os


print("================")
print("CLEAN MUSICXML V16")
print("================")


def quantize(q):

    values = [
        0.25,
        0.5,
        0.75,
        1,
        1.5,
        2,
        3,
        4
    ]

    return min(
        values,
        key=lambda x: abs(x-q)
    )


def fix_measure(measure):

    limit = 4.0

    total = 0

    new_elements = []


    for n in measure.notesAndRests:

        dur = quantize(
            float(n.duration.quarterLength)
        )


        # 已經超過小節
        if total >= limit:
            break


        # 最後剩餘拍數
        remain = limit - total


        if dur > remain:

            dur = remain


        if dur > 0:

            n.duration.quarterLength = dur

            new_elements.append(n)

            total += dur



    # 不足補休止符

    if total < limit:

        rest = music21.note.Rest()

        rest.duration.quarterLength = (
            limit-total
        )

        new_elements.append(rest)


    # 清空原小節

    for n in list(measure.notesAndRests):

        measure.remove(n)


    for n in new_elements:

        measure.insert(
            measure.offset,
            n
        )


def clean(input_file, output_file):

    print("input:",input_file)


    score = music21.converter.parse(
        input_file
    )


    print("remove voices")


    for part in score.parts:

        for v in list(
            part.recurse().getElementsByClass(
                music21.stream.Voice
            )
        ):

            v.activeSite.remove(v)



    print("remove chords")


    for part in score.parts:

        for chord in list(
            part.recurse().getElementsByClass(
                music21.chord.Chord
            )
        ):

            notes = chord.notes

            if notes:

                chord.activeSite.replace(
                    chord,
                    notes[-1]
                )



    print("quantize")


    for n in score.recurse().notesAndRests:

        n.duration.quarterLength = quantize(
            n.duration.quarterLength
        )



    print("force 4/4")


    for part in score.parts:

        for m in part.getElementsByClass(
            music21.stream.Measure
        ):

            m.timeSignature = (
                music21.meter.TimeSignature(
                    "4/4"
                )
            )



    print("fix measures")


    for part in score.parts:

        measures = part.getElementsByClass(
            music21.stream.Measure
        )

        for m in measures:

            fix_measure(m)



    print("remove empty measures")


    for part in score.parts:

        for m in list(
            part.getElementsByClass(
                music21.stream.Measure
            )
        ):

            if len(m.notesAndRests)==0:

                part.remove(m)



    print("write")


    score.write(
        "musicxml",
        fp=output_file
    )


    print(
        "DONE",
        output_file
    )



if __name__=="__main__":

    if len(sys.argv)<3:

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit(1)


    clean(
        sys.argv[1],
        sys.argv[2]
    )