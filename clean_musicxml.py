import sys
from music21 import converter


print("CLEAN VERSION 20260724 V6")


def clean(input_file, output_file):

    print("開始 clean MusicXML")


    score = converter.parse(input_file)


    for part in score.parts:

        for element in part.recurse().notesAndRests:


            ql = element.duration.quarterLength


            # jianpu_ly 不接受太短音符
            if ql < 0.5:

                element.duration.quarterLength = 0.5



            # 過長音符修正
            elif ql > 8:

                element.duration.quarterLength = 4



            # 重新連結 duration
            element.duration.linked = True



    score.write(
        "musicxml",
        fp=output_file
    )


    print(
        "clean完成"
    )

    print(
        output_file
    )



if __name__ == "__main__":


    if len(sys.argv) < 3:

        print(
            "使用方式:"
        )

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit(1)



    clean(
        sys.argv[1],
        sys.argv[2]
    )