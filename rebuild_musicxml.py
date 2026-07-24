import sys
import music21


print("REBUILD VERSION 20260724 V5")


def rebuild(input_file, output_file):

    print("開始重建 MusicXML")


    score = music21.converter.parse(
        input_file
    )


    # 修正拍號
    for ts in score.recurse().getElementsByClass(
        "TimeSignature"
    ):

        print(
            "原拍號:",
            ts.ratioString
        )


        if ts.denominator == 16:

            ts.numerator *= 1
            ts.denominator = 4


            print(
                "修正拍號:",
                ts.ratioString
            )



    # 修正音符長度
    for element in score.recurse():

        if hasattr(element, "duration"):

            ql = element.duration.quarterLength


            if ql <= 0:
                ql = 1


            if ql > 12:
                ql = 12


            element.duration.quarterLength = ql



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