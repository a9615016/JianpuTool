import sys
from music21 import converter, chord


print("CLEAN VERSION 20260724 V7")


def clean(input_file, output_file):

    print("開始 clean MusicXML")


    score = converter.parse(input_file)



    for part in score.parts:


        # 移除和弦，只留最高音(主旋律)
        for c in list(part.recurse().getElementsByClass('Chord')):

            n = c.notes[0]

            c.activeSite.replace(
                c,
                n
            )



        for element in list(part.recurse().notesAndRests):


            ql = element.duration.quarterLength


            if ql < 0.5:

                element.duration.quarterLength = 0.5



            if ql > 8:

                element.duration.quarterLength = 4



            element.duration.linked = True



    score.write(
        "musicxml",
        fp=output_file
    )


    print("clean完成")
    print(output_file)



if __name__ == "__main__":


    clean(
        sys.argv[1],
        sys.argv[2]
    )