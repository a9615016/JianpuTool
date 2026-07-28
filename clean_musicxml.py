from music21 import converter, stream, note, meter
import sys

VERSION = "CLEAN MUSICXML V83.1 PURE NOTE REBUILD FINAL"

print("######## USING V83.1 CLEANER ########")


def quantize_duration(d):

    values = [
        4.0,
        2.0,
        1.0,
        0.5,
        0.25,
        0.125
    ]

    x = float(d)

    return min(
        values,
        key=lambda v: abs(v-x)
    )


def extract_clean_notes(score):

    print("extract clean notes")

    result = []

    for n in score.recurse().notes:

        # only rebuild pitch notes
        new = note.Note()

        new.pitch = n.pitch

        dur = quantize_duration(
            n.duration.quarterLength
        )

        new.duration.quarterLength = dur

        # remove all notation
        new.tie = None
        new.expressions = []
        new.articulations = []
        new.beams = None

        result.append(new)


    return result



def rebuild_timeline(notes):

    print("rebuild timeline V83.1")


    score = stream.Score()

    part = stream.Part()


    part.append(
        meter.TimeSignature("4/4")
    )


    measure_no = 1

    measure = stream.Measure(
        number=measure_no
    )


    beat = 0.0


    for n in notes:


        remain = float(
            n.duration.quarterLength
        )


        while remain > 0:


            space = 4.0 - beat


            take = min(
                remain,
                space
            )


            new_note = note.Note(
                n.pitch
            )

            new_note.duration.quarterLength = take


            measure.append(
                new_note
            )


            beat += take

            remain -= take



            if abs(beat-4.0) < 0.0001:


                part.append(
                    measure
                )


                measure_no += 1


                measure = stream.Measure(
                    number=measure_no
                )


                beat = 0.0



    if beat > 0:


        rest = note.Rest()

        rest.duration.quarterLength = (
            4.0 - beat
        )

        measure.append(rest)


        part.append(measure)



    score.append(part)

    return score




def check(score):

    print("FINAL CHECK")


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


        if abs(total-4.0)>0.001:

            raise Exception(
                "BAD MEASURE"
            )


    print("ALL MEASURES SAFE")




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


    notes = extract_clean_notes(
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


    if len(sys.argv)<3:

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit()


    clean(
        sys.argv[1],
        sys.argv[2]
    )