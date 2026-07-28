# jianpu_fix_musicxml.py
# V14 CLEAN REBUILD
# 目的: 重新建立 jianpu_ly 可以吃的 MusicXML

import sys
import music21 as m21


def clean_score(input_file, output_file):

    print("V14 CLEAN REBUILD START")

    score = m21.converter.parse(input_file)

    # 取第一聲部（避免鋼琴左右手造成 jianpu 爆炸）
    parts = score.parts

    if len(parts) > 1:
        print("remove extra parts")
        score = parts[0]

    # 移除所有標記
    print("remove ties beams slurs")

    for n in score.recurse().notes:

        # tie
        n.tie = None

        # beams
        try:
            n.beams = m21.beam.Beams()
        except:
            pass

        # articulation
        n.articulations = []

        # lyric
        n.lyric = None


    # 移除休止特殊標記
    for r in score.recurse().rests:
        r.lyric = None


    print("flatten duration")

    # 重新量化節奏
    score = score.quantize(
        quarterLengthDivisors=[
            4,8,16
        ]
    )


    print("rebuild measures")

    # 強制4/4
    ts = m21.meter.TimeSignature("4/4")

    for p in score.parts:

        p.insert(0, ts)

        measures = p.makeMeasures()

        p.removeByClass('Measure')

        for m in measures:
            p.append(m)


    print("FINAL CHECK")

    for i,m in enumerate(score.parts[0].getElementsByClass(
        'Measure'
    )):

        dur = m.duration.quarterLength

        print(
            "Measure",
            i+1,
            float(dur)
        )


    print("WRITE")

    score.write(
        "musicxml",
        fp=output_file
    )

    print("DONE")
    print(output_file)



if __name__ == "__main__":

    if len(sys.argv)<3:
        print(
        "usage: python jianpu_fix_musicxml.py input.musicxml output.musicxml"
        )
        exit()


    clean_score(
        sys.argv[1],
        sys.argv[2]
    )