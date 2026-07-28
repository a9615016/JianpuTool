from music21 import converter, stream, note, meter
import sys

VERSION = "CLEAN MUSICXML V83.2 PURE TIMELINE REBUILD FINAL"


# ==========================
# duration quantize
# ==========================

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



# ==========================
# recreate note
# ==========================

def clone_note(n):

    if n.isRest:

        x = note.Rest()

    else:

        x = note.Note(
            n.pitch
        )


    x.duration.quarterLength = quantize_duration(
        n.duration.quarterLength
    )


    return x



# ==========================
# extract clean notes
# ==========================

def extract_notes(score):

    result=[]


    for n in score.recurse().notesAndRests:


        x = clone_note(n)


        result.append(x)


    return result




# ==========================
# rebuild timeline
# ==========================

def rebuild_timeline(notes):

    print(
        "######## USING V83.2 CLEANER ########"
    )


    score = stream.Score()

    part = stream.Part()


    part.insert(
        0,
        meter.TimeSignature("4/4")
    )


    measure_no = 1

    measure = stream.Measure(
        number=measure_no
    )


    beat = 0.0



    for n in notes:


        dur = float(
            n.duration.quarterLength
        )


        while beat + dur > 4.0:


            remain = 4.0 - beat


            if remain > 0:


                x = clone_note(n)

                x.duration.quarterLength = remain

                measure.insert(
                    beat,
                    x
                )


            part.append(
                measure
            )


            measure_no += 1


            measure = stream.Measure(
                number=measure_no
            )


            beat = 0.0


            dur -= remain



        if dur > 0:


            x = clone_note(n)

            x.duration.quarterLength = dur


            measure.insert(
                beat,
                x
            )


            beat += dur




    # last measure rest

    if beat < 4:

        r = note.Rest()

        r.duration.quarterLength = (
            4-beat
        )

        measure.insert(
            beat,
            r
        )


    part.append(
        measure
    )


    score.append(
        part
    )


    return score




# ==========================
# final check
# ==========================

def check(score):


    print(
        "FINAL CHECK"
    )


    for m in score.parts[0].getElementsByClass(
        "Measure"
    ):


        total=sum(
            float(x.duration.quarterLength)
            for x in m.notesAndRests
        )


        print(
            "Measure",
            m.number,
            total
        )


        if abs(total-4.0)>0.001:

            raise Exception(
                f"BAD MEASURE {m.number} {total}"
            )


    print(
        "ALL MEASURES SAFE"
    )




# ==========================
# clean
# ==========================

def clean(inp,out):


    print("================")
    print(VERSION)
    print("================")


    print("read")

    old = converter.parse(
        inp
    )


    print("extract pure notes")


    notes = extract_notes(
        old
    )


    print("rebuild pure timeline")


    score = rebuild_timeline(
        notes
    )


    print(
        "FORCE MAKE MEASURES"
    )


    score = score.makeMeasures(
        inPlace=False
    )


    score.stripTies(
        inPlace=True
    )


    check(
        score
    )


    print(
        "FINAL WRITE"
    )


    score.write(
        "musicxml",
        fp=out
    )


    print(
        "DONE"
    )

    print(out)




if __name__=="__main__":


    if len(sys.argv)<3:

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit()


    clean(
        sys.argv[1],
        sys.argv[2]
    )