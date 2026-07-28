# clean_musicxml.py
# V51 FINAL JIANPU OFFSET FIX

import sys
from music21 import converter, stream, note, chord, meter


def reset_offsets(score):
    print("reset note offsets")

    for part in score.parts:

        measures = part.getElementsByClass(stream.Measure)

        for m in measures:

            new_elements = []

            offset = 0.0

            for el in m.notesAndRests:

                dur = el.duration.quarterLength

                # 修正 offset
                el.offset = offset

                new_elements.append(el)

                offset += dur


            # 補滿 4/4
            remain = 4.0 - offset

            if remain > 0.001:

                r = note.Rest(
                    quarterLength=remain
                )

                r.offset = offset

                new_elements.append(r)


            # 清除舊內容
            m.removeByClass(
                ['Note',
                 'Rest',
                 'Chord']
            )


            for el in new_elements:
                m.insert(el.offset, el)


    return score



def clean_musicxml(src, dst):

    print("================")
    print("CLEAN MUSICXML V51")
    print("JIANPU OFFSET FIX")
    print("================")


    print("read")

    score = converter.parse(src)



    print("remove voices")

    for part in score.parts:
        for n in part.recurse():

            if hasattr(n, "voice"):
                n.voice = None



    print("remove chords")

    for part in score.parts:

        for c in part.recurse().getElementsByClass(chord.Chord):

            pitch = c.root()

            if pitch:

                n = note.Note(
                    pitch.pitch
                )

                n.duration = c.duration

                c.activeSite.replace(
                    c,
                    n
                )



    print("remove beams")

    for n in score.recurse().notes:

        n.beams = None



    print("remove ties")

    for n in score.recurse().notes:

        n.tie = None



    print("force 4/4")

    for part in score.parts:

        part.insert(
            0,
            meter.TimeSignature("4/4")
        )



    print("duration quantize")

    for n in score.recurse().notesAndRests:

        q = n.duration.quarterLength

        # 四分音符以下量化
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

        closest = min(
            values,
            key=lambda x: abs(x-q)
        )

        n.duration.quarterLength = closest



    print("rebuild measures")

    score.makeMeasures(
        inPlace=True
    )



    print("reset note offsets")

    score = reset_offsets(score)



    print("clear notation cache")

    score.coreElementsChanged()



    print("FINAL CHECK")


    ok = True

    for i,m in enumerate(
        score.parts[0].getElementsByClass(stream.Measure),
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


        if abs(total-4.0)>0.01:

            ok=False



    if ok:

        print("ALL MEASURES SAFE")

    else:

        print("WARNING measure mismatch")



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