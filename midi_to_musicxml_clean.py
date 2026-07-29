# midi_to_musicxml_clean.py v7.1
# JianpuTool FINAL CLEANER

import sys
from music21 import converter, stream, note, meter, tempo


BEAT = 4.0


# =========================
# duration quantize
# =========================

def quantize_duration(x):

    values = [
        4.0,      # whole
        3.0,      # dotted half
        2.0,      # half
        1.5,
        1.0,      # quarter
        0.75,
        0.5,      # eighth
        0.25,     # sixteenth
        0.125
    ]

    return min(
        values,
        key=lambda v: abs(v-x)
    )



# =========================
# clean note
# =========================

def clean_element(e):

    if isinstance(e, note.Note):

        n = note.Note(e.pitch)

        n.duration.quarterLength = (
            quantize_duration(
                e.duration.quarterLength
            )
        )

        # remove tie

        n.tie = None

        return n


    if isinstance(e, note.Rest):

        r = note.Rest()

        r.duration.quarterLength = (
            quantize_duration(
                e.duration.quarterLength
            )
        )

        return r


    return None



# =========================
# rebuild measure
# =========================

def rebuild_measure(m):

    new_m = stream.Measure(
        number=m.number
    )


    used = 0.0


    for e in m.flatten().notesAndRests:

        obj = clean_element(e)


        if obj is None:
            continue


        dur = obj.duration.quarterLength


        # 超過小節

        if used + dur > BEAT:

            remain = BEAT-used


            if remain > 0:

                r = note.Rest()

                r.duration.quarterLength = (
                    quantize_duration(remain)
                )

                new_m.append(r)


            break



        new_m.append(obj)

        used += dur



    # 不足補 rest

    if used < BEAT:

        r = note.Rest()

        r.duration.quarterLength = (
            quantize_duration(
                BEAT-used
            )
        )

        new_m.append(r)



    return new_m



# =========================
# clean part
# =========================

def clean_part(part):

    p = stream.Part()

    p.id = part.id


    p.append(
        meter.TimeSignature("4/4")
    )


    for m in part.getElementsByClass(
        stream.Measure
    ):

        p.append(
            rebuild_measure(m)
        )


    return p



# =========================
# main convert
# =========================

def convert(
    midi_file,
    output_file
):

    print("LOAD MIDI")

    score = converter.parse(
        midi_file
    )


    print("CLEAN")

    out = stream.Score()


    # tempo

    for t in score.flatten().getElementsByClass(
        tempo.MetronomeMark
    ):

        out.append(t)



    for part in score.parts:

        print(
            "PART:",
            part.id
        )

        out.append(
            clean_part(part)
        )



    print("FINAL CHECK")


    for p in out.parts:

        for m in p.getElementsByClass(
            stream.Measure
        ):

            print(
                "Measure",
                m.number,
                m.duration.quarterLength
            )


    print("WRITE MUSICXML")


    out.write(
        "musicxml",
        fp=output_file
    )


    print("DONE")
    print(output_file)



if __name__ == "__main__":

    if len(sys.argv)<3:

        print(
            "python midi_to_musicxml_clean.py input.mid output.musicxml"
        )

        sys.exit(1)


    convert(
        sys.argv[1],
        sys.argv[2]
    )