from music21 import converter, stream, note, meter
import sys
import copy

VERSION = "CLEAN MUSICXML V83.1 HARD TIMELINE RESET FINAL"


def quantize_duration(d):

    x = float(d)

    # 1/16 beat grid
    q = round(x * 16) / 16

    if q <= 0:
        q = 0.25

    return q



def extract_notes(score):

    result = []

    for n in score.recurse().notesAndRests:

        item = copy.deepcopy(n)

        # remove bad notation
        item.expressions = []

        if hasattr(item, "lyrics"):
            item.lyrics = []

        dur = quantize_duration(
            item.duration.quarterLength
        )

        item.duration.quarterLength = dur

        result.append(item)


    return result



def new_measure(number):

    m = stream.Measure(
        number=number
    )

    m.insert(
        0,
        meter.TimeSignature("4/4")
    )

    return m



def rebuild_timeline(notes):

    print("rebuild timeline")


    score = stream.Score()

    part = stream.Part()


    measure_no = 1

    current_measure = new_measure(
        measure_no
    )


    beat = 0.0


    for n in notes:

        dur = float(
            n.duration.quarterLength
        )


        while beat + dur > 4.0:

            remain = 4.0 - beat


            if remain > 0:

                left = copy.deepcopy(n)

                left.duration.quarterLength = remain

                current_measure.append(
                    left
                )


            part.append(
                current_measure
            )


            measure_no += 1

            current_measure = new_measure(
                measure_no
            )


            beat = 0.0

            dur -= remain


            if dur <= 0:
                break



        if dur > 0:

            right = copy.deepcopy(n)

            right.duration.quarterLength = dur

            current_measure.append(
                right
            )

            beat += dur



    # fill last measure

    if beat < 4:

        rest = note.Rest()

        rest.duration.quarterLength = (
            4 - beat
        )

        current_measure.append(
            rest
        )


    part.append(
        current_measure
    )


    score.append(
        part
    )


    return score



def check(score):

    print("FINAL CHECK")


    for m in score.parts[0].getElementsByClass(
        "Measure"
    ):

        total = sum(
            float(x.duration.quarterLength)
            for x in m.notesAndRests
        )


        print(
            "Measure",
            m.number,
            total
        )


        if abs(total-4.0) > 0.001:

            raise Exception(
                f"BAD MEASURE {m.number}: {total}"
            )


    print(
        "ALL MEASURES SAFE"
    )



def clean(inp,out):

    print("================")
    print(VERSION)
    print("================")


    print("read")

    old = converter.parse(inp)


    print("remove voices")
    print("remove chords")
    print("remove beams")
    print("remove ties")


    notes = extract_notes(
        old
    )


    new_score = rebuild_timeline(
        notes
    )


    check(
        new_score
    )


    print("FINAL WRITE")


    new_score.write(
        "musicxml",
        fp=out
    )


    print("DONE")
    print(out)



if __name__ == "__main__":

    if len(sys.argv) < 3:

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit()


    clean(
        sys.argv[1],
        sys.argv[2]
    )