import music21
import sys


def rebuild(input_file, output_file):

    print("開始重建 MusicXML")


    score = music21.converter.parse(input_file)


    # ======================
    # 只保留第一聲部
    # ======================

    if len(score.parts) > 0:
        part = score.parts[0]
    else:
        part = score



    # ======================
    # 移除 spanner
    # ======================

    for sp in list(part.spannerBundle):

        try:
            sp.activeSite = None

        except:
            pass



    # ======================
    # 修正 duration
    # ======================

    allowed = [
        0.25,   # 16分音符
        0.5,    # 8分音符
        0.75,
        1,      # 四分音符
        1.5,
        2,      # 二分音符
        3,
        4,      # 全音符
        6,
        8
    ]



    for item in part.recurse().notesAndRests:


        try:

            ql = float(
                item.duration.quarterLength
            )

        except:

            ql = 1



        # 避免非法長度

        if ql <= 0:

            ql = 1



        # 找最近合法拍值

        value = min(
            allowed,
            key=lambda x: abs(x - ql)
        )



        item.duration.quarterLength = value



    # ======================
    # octave限制
    # ======================

    for note in part.recurse().notes:


        if note.pitch.octave < 3:

            note.pitch.octave = 3


        if note.pitch.octave > 6:

            note.pitch.octave = 6



    # ======================
    # 強制 4/4
    # ======================

    part.insert(
        0,
        music21.meter.TimeSignature("4/4")
    )



    # ======================
    # 輸出
    # ======================

    print("輸出 MusicXML")


    part.write(
        "musicxml",
        fp=output_file
    )


    print(
        "完成",
        output_file
    )



if __name__ == "__main__":


    if len(sys.argv) < 3:

        print(
            "使用方式:"
            "python rebuild_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit()



    rebuild(
        sys.argv[1],
        sys.argv[2]
    )