import sys
from music21 import converter
from music21 import meter
from music21 import stream
from music21 import note


def clean_musicxml(input_file, output_file):

    print("開始 MusicXML 清理")

    score = converter.parse(input_file)


    # ==========================
    # 每個 part
    # ==========================

    for part in score.parts:


        # 移除 voice
        part.flattenUnnecessaryVoices()


        measures = part.getElementsByClass(
            stream.Measure
        )


        for m in measures:


            # 強制 4/4

            m.timeSignature = meter.TimeSignature(
                "4/4"
            )


            # 移除 offset 異常元素

            remove=[]


            for e in m.notesAndRests:


                if e.offset < 0:

                    remove.append(e)


                if e.duration.quarterLength <=0:

                    remove.append(e)



            for e in remove:

                m.remove(e)



        # ======================
        # 重新補小節
        # ======================

        part.makeMeasures(
            inPlace=True
        )



    # ==========================
    # 再一次修正
    # ==========================


    for part in score.parts:

        for m in part.getElementsByClass(
            stream.Measure
        ):

            m.leftBarline = None
            m.rightBarline = None



    score.write(
        "musicxml",
        fp=output_file
    )


    print(
        "clean完成",
        output_file
    )




if __name__=="__main__":


    if len(sys.argv)<3:

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        exit()



    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )