# jianpu_prepare_v3.py
# JianpuTool V3 FINAL PREPARE

import sys
from music21 import converter, stream, note, chord, meter


def fix_measure(measure):

    target = 4.0   # 4/4

    total = 0

    for n in measure.notesAndRests:
        total += n.duration.quarterLength


    # 超過小節 -> 壓縮
    if total > target:

        ratio = target / total

        for n in measure.notesAndRests:
            n.duration.quarterLength *= ratio


    # 不足補休止
    elif total < target:

        r = note.Rest()
        r.duration.quarterLength = target-total
        measure.append(r)


def prepare(src, dst):

    print("######## JIANPU PREPARE V3 ########")

    score = converter.parse(src)


    # 強制4/4
    for p in score.parts:

        p.insert(
            0,
            meter.TimeSignature("4/4")
        )


        measures = p.makeMeasures()

        print(
            "MEASURES:",
            len(measures)
        )


        for i,m in enumerate(measures):

            fix_measure(m)

            length = sum(
                n.duration.quarterLength
                for n in m.notesAndRests
            )

            print(
                "Measure",
                i+1,
                length
            )


        p.measureOffsetMap = None


    # 清理
    for p in score.parts:

        for m in p.getElementsByClass("Measure"):

            for n in m.notes:

                if isinstance(n, chord.Chord):

                    n = n.notes[0]


    score.write(
        "musicxml",
        fp=dst
    )


    print("######## V3 DONE ########")
    print(dst)



if __name__=="__main__":

    if len(sys.argv)<3:
        print(
            "usage: python jianpu_prepare_v3.py input.xml output.xml"
        )
        exit()


    prepare(
        sys.argv[1],
        sys.argv[2]
    )