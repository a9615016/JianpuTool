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


                # 修正非法長度
                if ql <= 0:
                    ql = 1


                # jianpu_ly 不支援超長音符
                if ql > 12:
                    ql = 12


                try:

                    element.duration.quarterLength = ql

                except Exception:

                    pass



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


    if len(sys.argv) < 3:

        print(
            "使用方式:"
        )

        print(
            "python rebuild_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit(1)



    rebuild(
        sys.argv[1],
        sys.argv[2]
    )