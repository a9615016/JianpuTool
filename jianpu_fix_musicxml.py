import sys
from music21 import converter, stream, note, meter, duration, chord


VERSION = "JIANPU FIX MUSICXML V5.0"


# 四分音符比例
VALID_DURATIONS = [
    4.0,
    2.0,
    1.0,
    0.5,
    0.25,
    0.125
]


def snap_duration(q):
    """
    將 duration 修正成 jianpu_ly 可接受值
    """

    return min(
        VALID_DURATIONS,
        key=lambda x: abs(x - q)
    )


def remove_bad_elements(score):

    print("remove chords")

    for el in score.recurse():

        if isinstance(el, chord.Chord):
            n = note.Note(
                el.root().pitch
            )
            n.duration = el.duration
            el.activeSite.replace(el, n)


    print("remove ties")

    for n in score.recurse().notes:

        if hasattr(n, "tie"):
            n.tie = None



def quantize_notes(score):

    print("duration quantize")

    for n in score.recurse().notes:

        if isinstance(n, note.Note):

            q = float(n.duration.quarterLength)

            new_q = snap_duration(q)

            n.duration = duration.Duration(new_q)



def force_time_signature(score):

    print("force 4/4")

    for p in score.parts:

        p.insert(
            0,
            meter.TimeSignature("4/4")
        )



def rebuild_measures(score):

    print("rebuild measures")

    score.makeMeasures(
        inPlace=True
    )



def fix_measure_lengths(score):

    print("fix measure lengths")

    for p in score.parts:

        for m in list(p.getElementsByClass("Measure")):

            total = sum(
                n.duration.quarterLength
                for n in m.notesAndRests
            )


            diff = 4.0 - float(total)


            # 太長
            if diff < 0:

                remain = 4.0

                for n in list(m.notesAndRests):

                    if remain <= 0:
                        break

                    if n.duration.quarterLength <= remain:

                        remain -= n.duration.quarterLength

                    else:

                        n.duration = duration.Duration(
                            remain
                        )

                        remain = 0


            # 太短補休止
            elif diff > 0:

                r = note.Rest()

                r.duration = duration.Duration(
                    diff
                )

                m.append(r)



def final_check(score):

    print("FINAL CHECK")

    ok = True

    for p in score.parts:

        for i,m in enumerate(
            p.getElementsByClass("Measure"),
            start=1
        ):

            total = sum(
                n.duration.quarterLength
                for n in m.notesAndRests
            )


            print(
                "Measure",
                i,
                float(total)
            )


            if abs(float(total)-4.0) > 0.01:

                ok=False


    if ok:
        print("ALL MEASURES SAFE")
    else:
        print("WARNING measure mismatch")



def main():

    if len(sys.argv)<3:

        print(
            "python jianpu_fix_musicxml.py input.musicxml output.musicxml"
        )

        return


    src=sys.argv[1]
    dst=sys.argv[2]


    print("================")
    print(VERSION)
    print("================")


    score=converter.parse(src)


    remove_bad_elements(score)

    force_time_signature(score)

    quantize_notes(score)

    rebuild_measures(score)

    fix_measure_lengths(score)

    rebuild_measures(score)


    final_check(score)


    print("FINAL WRITE")

    score.write(
        "musicxml",
        fp=dst
    )


    print("DONE")
    print(dst)



if __name__=="__main__":
    main()