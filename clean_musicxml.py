# clean_musicxml.py
# CLEAN MUSICXML V33 PDF COMPATIBLE

from music21 import converter, stream, note, chord, meter, bar
import sys


print("================")
print("CLEAN MUSICXML V33 PDF COMPATIBLE")
print("================")


def quantize_duration(q):

    allowed = [
        0.25,   # 16分
        0.5,    # 8分
        1.0,    # 4分
        2.0,    # 2分
        4.0     # 全音
    ]

    return min(
        allowed,
        key=lambda x: abs(x-q)
    )


def clean_musicxml(src, dst):

    print("read")

    score = converter.parse(src)


    # 只保留第一聲部
    print("remove voices")

    if len(score.parts) > 1:
        score = stream.Score(
            [score.parts[0]]
        )


    part = score.parts[0]


    print("remove chords")

    # chord 改單音最高音
    for c in list(part.recurse().getElementsByClass(chord.Chord)):

        n = note.Note(
            c.pitches[-1]
        )

        n.duration = c.duration

        c.activeSite.replace(
            c,
            n
        )


    print("remove ties")
    print("remove beams")


    for n in part.recurse().notes:

        if isinstance(n, note.Note):

            n.tie = None
            n.beams = []

            # 移除裝飾
            n.articulations = []
            n.expressions = []


            # 節奏修正
            n.duration.quarterLength = quantize_duration(
                float(n.duration.quarterLength)
            )



    print("force 4/4")


    part.insert(
        0,
        meter.TimeSignature("4/4")
    )


    print("rebuild measures")


    score = score.makeMeasures()


    print("split cross measure notes")


    # 再次切斷跨小節音符
    score = score.makeMeasures(
        inPlace=False
    )


    print("fill measure rest")


    score.makeRests(
        fillGaps=True,
        inPlace=True
    )


    print("clear notation cache")


    for n in score.recurse().notes:

        if hasattr(n, "beams"):
            n.beams = []

        if hasattr(n, "tie"):
            n.tie = None



    print("FINAL CHECK")


    bad = False


    for i,m in enumerate(
        score.parts[0].getElementsByClass("Measure"),
        1
    ):

        length = float(
            m.duration.quarterLength
        )

        print(
            "Measure",
            i,
            length
        )


        if length > 4.0001:
            bad=True



    if bad:

        print(
            "WARNING measure mismatch"
        )

    else:

        print(
            "ALL MEASURES SAFE"
        )



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
        sys.exit()


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )