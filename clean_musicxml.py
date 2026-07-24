import sys
from music21 import converter


print("CLEAN VERSION 20260724 V5")


def clean(input_file, output_file):

    print("開始 clean MusicXML")


    score = converter.parse(input_file)


    for part in score.parts:


        for note in part.recurse().notesAndRests:


            ql = note.duration.quarterLength


            # jianpu_ly 不接受超短音符
            if ql < 0.5:

                note.duration.quarterLength = 0.5


            # 修正怪長度
            if ql > 8:

                note.duration.quarterLength = 4



    score.write(
        "musicxml",
        fp=output_file
    )


    print(
        "clean完成",
        output_file
    )



if __name__ == "__main__":

    clean(
        sys.argv[1],
        sys.argv[2]
    )