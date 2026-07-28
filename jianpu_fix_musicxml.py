# jianpu_fix_musicxml.py
# V8.0 STRICT JIANPU COMPATIBLE

import sys
from music21 import converter, stream, note, meter, duration, chord


def remove_bad_elements(score):

    print("remove voices")

    for part in score.parts:

        for el in list(part.recurse()):

            if isinstance(el, chord.Chord):
                print("remove chord")
                n = note.Note(
                    el.pitches[0],
                    quarterLength=el.duration.quarterLength
                )
                el.activeSite.replace(el, n)

            elif isinstance(el, note.Note):

                if el.tie:
                    el.tie = None

                el.beams = None


def quantize_note(n):

    q = n.duration.quarterLength

    table = [
        0.25,
        0.5,
        0.75,
        1.0,
        1.5,
        2.0,
        3.0,
        4.0
    ]

    best = min(
        table,
        key=lambda x: abs(x-q)
    )

    n.duration = duration.Duration(best)



def rebuild_part(part):

    print("STRICT REBUILD MEASURES")

    new_part = stream.Part()

    new_part.append(
        meter.TimeSignature("4/4")
    )


    current_measure = stream.Measure()
    current_measure.number = 1

    used = 0


    for n in part.recurse().notesAndRests:

        if isinstance(n, note.Rest):
            continue


        quantize_note(n)

        length = n.duration.quarterLength


        while length > 0:

            remain = 4 - used


            if length <= remain:

                nn = n.clone()
                nn.duration = duration.Duration(length)

                current_measure.append(nn)

                used += length
                length = 0


            else:

                nn = n.clone()

                nn.duration = duration.Duration(remain)

                current_measure.append(nn)


                print(
                    "split note",
                    remain
                )


                length -= remain

                new_part.append(current_measure)

                current_measure = stream.Measure()

                current_measure.number += 1

                used = 0


        if used == 4:

            new_part.append(current_measure)

            current_measure = stream.Measure()

            current_measure.number += 1

            used = 0



    # 補最後小節

    if used < 4:

        r = note.Rest(
            quarterLength=4-used
        )

        current_measure.append(r)


    if len(current_measure.notesAndRests)>0:
        new_part.append(current_measure)


    return new_part



def final_check(score):

    print("FINAL CHECK")

    ok=True

    for m in score.parts[0].getElementsByClass(
        "Measure"
    ):

        total = sum(
            x.duration.quarterLength
            for x in m.notesAndRests
        )

        print(
            "Measure",
            m.number,
            total
        )

        if abs(total-4)>0.01:
            ok=False


    if ok:
        print(
            "ALL MEASURES SAFE"
        )
    else:
        print(
            "WARNING measure mismatch"
        )



def fix(input_file, output_file):

    print("================")
    print(
        "JIANPU FIX MUSICXML V8.0"
    )
    print("================")


    score = converter.parse(
        input_file
    )


    print("read")


    score.remove(
        score.parts[0].recurse().getElementsByClass(
            meter.TimeSignature
        )
    )


    remove_bad_elements(score)


    fixed = stream.Score()


    for p in score.parts:

        np = rebuild_part(p)

        fixed.append(np)



    print("clear cache")


    fixed.write(
        "musicxml",
        fp=output_file
    )


    final_check(
        fixed
    )


    print("DONE")
    print(output_file)



if __name__=="__main__":

    if len(sys.argv)<3:

        print(
            "python jianpu_fix_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit()


    fix(
        sys.argv[1],
        sys.argv[2]
    )