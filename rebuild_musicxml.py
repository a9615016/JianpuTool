import music21
import sys


def rebuild(input_file, output_file):

    print("開始重建 MusicXML")


    score = music21.converter.parse(input_file)


    # 只取第一聲部

    if len(score.parts) > 0:
        part = score.parts[0]
    else:
        part = score



    # 移除不規則 spanner
    for sp in list(part.spannerBundle):
        sp.activeSite = None



    allowed = [
        0.25,
        0.5,
        1,
        1.5,
        2,
        3,
        4,
        6,
        8
    ]



    for item in part.recurse().notesAndRests:


        ql = item.duration.quarterLength


        try:

            ql = float(ql)

        except:

            ql = 1



        if ql <= 0:

            ql = 1



        # 找最近合法拍值

        value = min(
            allowed,
            key=lambda x:abs(x-ql)
        )


        item.duration.quarterLength = value



        # 強制重新計算 duration

        item.duration.type = None
        item.duration.quarterLength = value



    # 清除 metadata

    part.metadata = None



    # 4/4

    part.insert(
        0,
        music21.meter.TimeSignature("4/4")
    )



    print("輸出 MusicXML")

    part.write(
        "musicxml",
        fp=output_file
    )


    print(
        "完成",
        output_file
    )



if __name__=="__main__":


    rebuild(
        sys.argv[1],
        sys.argv[2]
    )