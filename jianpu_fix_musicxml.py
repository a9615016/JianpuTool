import sys
from music21 import converter, stream, note, chord, meter, duration


TICKS_PER_BEAT = 16
BAR_TICKS = 64


def quantize_duration(q):

    # quarterLength -> ticks
    ticks = round(q * TICKS_PER_BEAT)

    allowed = [
        4,    # quarter
        8,    # half
        12,   # dotted quarter
        16,   # whole
        2,    # eighth
        1
    ]

    if ticks <= 1:
        return 0.0625

    best = min(
        allowed,
        key=lambda x: abs(x - ticks)
    )

    return best / TICKS_PER_BEAT



def remove_chords(s):

    for el in list(s.recurse()):

        if isinstance(el, chord.Chord):

            n = note.Note(
                el.pitch
            )

            n.duration = el.duration

            el.activeSite.replace(
                el,
                n
            )



def clean_notes(s):

    for n in s.recurse().notes:

        if isinstance(n, note.Note):

            n.duration.type = None

            n.duration.quarterLength = (
                quantize_duration(
                    n.duration.quarterLength
                )
            )

            n.tie = None



def rebuild_measure(part):

    measures = []

    current = stream.Measure()

    length = 0


    for el in part.flatten().notesAndRests:

        q = el.duration.quarterLength


        if length + q > 4:

            rest_time = 4 - length

            if rest_time > 0:

                current.append(
                    note.Rest(
                        quarterLength=rest_time
                    )
                )

            measures.append(current)

            current = stream.Measure()

            length = 0


        current.append(el)

        length += q



    if length < 4:

        current.append(
            note.Rest(
                quarterLength=4-length
            )
        )


    measures.append(current)


    return measures



def fix_musicxml(src, dst):

    print("================")
    print("JIANPU FIX MUSICXML V4.0")
    print("================")


    score = converter.parse(src)


    print("remove chords")

    remove_chords(score)


    print("remove ties/beams")

    for el in score.recurse():

        if hasattr(el, "tie"):
            el.tie = None



    print("duration quantize")

    clean_notes(score)



    print("force 4/4")

    for p in score.parts:

        p.insert(
            0,
            meter.TimeSignature("4/4")
        )



    print("rebuild measures")


    new_score = stream.Score()


    for p in score.parts:

        new_part = stream.Part()


        for m in rebuild_measure(p):

            new_part.append(m)


        new_score.append(new_part)



    print("final check")


    for i,m in enumerate(
        new_score.parts[0].getElementsByClass(
            stream.Measure
        ),
        1
    ):

        total = sum(
            x.duration.quarterLength
            for x in m.notesAndRests
        )

        print(
            "Measure",
            i,
            total
        )


    print("write")

    new_score.write(
        "musicxml",
        fp=dst
    )


    print("DONE")
    print(dst)



if __name__ == "__main__":

    if len(sys.argv) < 3:

        print(
            "usage: python jianpu_fix_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit()


    fix_musicxml(
        sys.argv[1],
        sys.argv[2]
    )