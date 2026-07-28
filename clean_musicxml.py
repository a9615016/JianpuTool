# CLEAN MUSICXML V40
# Jianpu compatible
# Render + music21 + BasicPitch

import sys
import copy
from music21 import converter, stream, meter, note, chord, tie


TARGET_BEAT = 4.0


def quantize_duration(d):

    values = [
        4.0,
        2.0,
        1.5,
        1.0,
        0.75,
        0.5,
        0.25
    ]

    best = min(
        values,
        key=lambda x: abs(x-d)
    )

    return best



def remove_problem_objects(score):

    print("remove voices")

    for p in score.parts:
        for n in p.recurse():
            if hasattr(n, "voices"):
                try:
                    n.voices.clear()
                except:
                    pass


    print("remove chords")

    for p in score.parts:

        for c in list(
            p.recurse().getElementsByClass("Chord")
        ):
            n = note.Note(
                c.root()
            )
            n.duration = c.duration
            c.activeSite.replace(
                c,
                n
            )


    print("remove ties")

    for n in score.recurse().notes:

        if n.tie:
            n.tie = None



def force_44(score):

    print("force 4/4")

    for p in score.parts:

        p.insert(
            0,
            meter.TimeSignature("4/4")
        )



def quantize_notes(score):

    print("duration quantize")

    for n in score.recurse().notesAndRests:

        n.duration.quarterLength = (
            quantize_duration(
                float(
                    n.duration.quarterLength
                )
            )
        )



def rebuild_measures(score):

    print("rebuild measures")

    new_score = stream.Score()

    for part in score.parts:

        new_part = stream.Part()

        new_part.append(
            meter.TimeSignature("4/4")
        )

        beat = 0
        measure_no = 1

        m = stream.Measure(
            number=measure_no
        )


        for n in part.recurse().notesAndRests:

            dur = float(
                n.duration.quarterLength
            )


            if beat + dur > TARGET_BEAT:

                remain = TARGET_BEAT - beat


                if remain > 0:

                    n1 = copy.deepcopy(n)
                    n1.duration.quarterLength = remain

                    m.append(n1)


                print(
                    "split cross measure notes"
                )

                new_score_part = None


                new_part.append(m)


                measure_no += 1

                m = stream.Measure(
                    number=measure_no
                )


                n2 = copy.deepcopy(n)

                n2.duration.quarterLength = (
                    dur - remain
                )

                m.append(n2)


                beat = dur - remain


            else:

                m.append(
                    copy.deepcopy(n)
                )

                beat += dur


            if abs(beat - TARGET_BEAT) < 0.001:

                new_part.append(m)

                measure_no += 1

                m = stream.Measure(
                    number=measure_no
                )

                beat = 0


        if len(m.notesAndRests) > 0:

            rest = note.Rest(
                quarterLength=
                TARGET_BEAT-beat
            )

            m.append(rest)

            new_part.append(m)


        new_score.append(new_part)


    return new_score



def final_check(score):

    print("FINAL CHECK")

    ok = True

    for p in score.parts:

        for m in p.getElementsByClass(
            stream.Measure
        ):

            length = float(
                m.duration.quarterLength
            )

            print(
                "Measure",
                m.number,
                length
            )

            if abs(length-4.0)>0.01:

                ok=False


    if ok:
        print("ALL MEASURES SAFE")
    else:
        print("WARNING measure mismatch")



def clean_musicxml(src,dst):

    print("================")
    print("CLEAN MUSICXML V40")
    print("================")


    print("read")

    score = converter.parse(src)


    remove_problem_objects(score)

    force_44(score)

    quantize_notes(score)

    score = rebuild_measures(score)


    print("fill measure rest")

    final_check(score)


    print("clear notation cache")

    score.removeInvalid()


    print("FINAL WRITE")


    score.write(
        "musicxml",
        fp=dst
    )


    print("DONE")
    print(dst)



if __name__ == "__main__":

    if len(sys.argv)<3:

        print(
            "usage: python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit(1)


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )