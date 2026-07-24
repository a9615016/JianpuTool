import sys
from music21 import converter, stream, meter


print("REBUILD VERSION 20260724 V4")


def rebuild(input_file, output_file):

    print("開始重建 MusicXML")

    score = converter.parse(input_file)


    for part in score.parts:

        # 強制 4/4
        part.insert(
            0,
            meter.TimeSignature("4/4")
        )


        for measure in part.getElementsByClass(
            stream.Measure
        ):

            # 修正怪 duration
            for element in measure.notesAndRests:

                ql = element.duration.quarterLength


                # 不合法長度修正
                if ql > 4:

                    element.duration.quarterLength = 4


                # 強制重新計算 type
                element.duration.linked = True



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