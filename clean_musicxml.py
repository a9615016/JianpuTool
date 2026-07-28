# CLEAN MUSICXML V27
# FINAL JIANPU_LY BARCHECK FIX

import sys
from music21 import converter, stream, note, chord, meter, duration


TARGET_BEAT = 4.0


def log(x):
    print(x)


def remove_bad_elements(score):

    log("remove voices")
    log("remove chords")
    log("remove beams")
    log("remove ties")

    for part in score.parts:

        for n in list(part.recurse()):

            if isinstance(n, chord.Chord):
                n2 = note.Note(
                    n.pitches[0],
                    quarterLength=n.duration.quarterLength
                )
                n.activeSite.replace(n, n2)

            if isinstance(n, note.Note):
                n.tie = None
                n.beams = []

    return score



def quantize_notes(score):

    log("duration quantize")

    allowed = [
        0.25,
        0.5,
        1.0,
        2.0,
        4.0
    ]

    for n in score.recurse().notes:

        q = n.duration.quarterLength

        best = min(
            allowed,
            key=lambda x: abs(x-q)
        )

        n.duration = duration.Duration(best)

    return score



def rebuild_measure(part):

    log("rebuild measures")

    old_notes = list(part.recurse().notesAndRests)

    new_part = stream.Part()

    new_part.append(meter.TimeSignature("4/4"))

    current = 0

    measure = stream.Measure(
        number=1
    )

    measure_time = 0


    for n in old_notes:

        length = float(n.duration.quarterLength)


        # split over bar
        while measure_time + length > TARGET_BEAT:

            remain = TARGET_BEAT - measure_time

            if remain > 0:

                nn = n.clone()
                nn.duration = duration.Duration(remain)

                measure.append(nn)


            new_part.append(measure)

            log(
                f"Measure {measure.number} 4.0"
            )


            measure = stream.Measure(
                number=measure.number + 1
            )

            length -= remain
            measure_time = 0


            n = n.clone()
            n.duration = duration.Duration(length)


        measure.append(n)

        measure_time += length


        if abs(measure_time-TARGET_BEAT) < 0.001:

            new_part.append(measure)

            log(
                f"Measure {measure.number} 4.0"
            )

            measure = stream.Measure(
                number=measure.number+1
            )

            measure_time = 0



    # fill last measure

    if measure_time < TARGET_BEAT:

        r = note.Rest()

        r.duration = duration.Duration(
            TARGET_BEAT-measure_time
        )

        measure.append(r)


    new_part.append(measure)


    return new_part



def final_check(score):

    log("FINAL CHECK")


    for i,m in enumerate(
        score.parts[0].getElementsByClass(stream.Measure),
        1
    ):

        length = float(
            m.duration.quarterLength
        )

        log(
            f"Measure {i} {length}"
        )


        if abs(length-4.0)>0.01:

            raise Exception(
                f"Measure {i} BAD {length}"
            )


    log("ALL MEASURES SAFE")



def clean(inp,out):

    print("================")
    print("CLEAN MUSICXML V27 FINAL")
    print("================")


    log("read")

    score = converter.parse(inp)


    score = remove_bad_elements(score)


    score = quantize_notes(score)


    parts=[]

    for p in score.parts:

        parts.append(
            rebuild_measure(p)
        )


    score = stream.Score(parts)


    log("clear notation cache")

    score.makeNotation(
        inPlace=True
    )


    final_check(score)


    log("FINAL WRITE")


    score.write(
        "musicxml",
        fp=out
    )


    log("DONE")
    print(out)



if __name__=="__main__":

    if len(sys.argv)<2:
        print(
            "python clean_musicxml_v27.py input.musicxml output.musicxml"
        )
        sys.exit()


    inp=sys.argv[1]

    if len(sys.argv)>=3:
        out=sys.argv[2]
    else:
        out="clean.musicxml"


    clean(inp,out)