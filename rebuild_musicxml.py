import sys
import music21


print("REBUILD VERSION 20260724 V4")


def rebuild(input_file, output_file):

    print("開始重建 MusicXML")

    score = music21.converter.parse(
        input_file
    )


    for part in score.parts:

        for element in part.flatten():

            if hasattr(element, "duration"):

                ql = element.duration.quarterLength


                # 修正超長 duration
                if ql > 12:

                    element.duration.quarterLength = 12


                # 修正不合法 duration
                if ql == 0:

                    element.duration.quarterLength = 1



                # 拆除 complex duration
                element.duration.clear()


                element.duration.quarterLength = ql



    print("輸出 MusicXML")


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