import sys
from music21 import converter, meter, stream


print("REBUILD VERSION 20260724 V5")


def rebuild(input_file, output_file):

    print("開始重建 MusicXML")

    score = converter.parse(input_file)


    for part in score.parts:


        # 移除所有原本拍號
        for ts in part.recurse().getElementsByClass(
            meter.TimeSignature
        ):
            ts.activeSite.remove(ts)


        # 強制 4/4
        part.insert(
            0,
            meter.TimeSignature("4/4")
        )


        for measure in part.getElementsByClass(
            stream.Measure
        ):


            for item in measure.notesAndRests:


                ql = item.duration.quarterLength


                # 防止超長
                if ql > 4:
                    item.duration.quarterLength = 4


                # 修正非法 duration
                if ql <= 0:
                    item.duration.quarterLength = 1



                # 重新切割 duration
                item.duration.splitDot = False



    score.write(
        "musicxml",
        fp=output_file
    )


    print(
        "完成",
        output_file
    )



if __name__ == "__main__":

    rebuild(
        sys.argv[1],
        sys.argv[2]
    )