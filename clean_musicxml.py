import sys
from music21 import converter
from music21 import meter
from music21 import stream
from music21 import note
from music21 import chord


def clean_musicxml(input_file, output_file):

    print("開始 MusicXML 清理")

    score = converter.parse(input_file)


    # ==========================
    # 處理每個聲部
    # ==========================

    for part in score.parts:


        # 移除多餘 voice

        try:
            part.flattenUnnecessaryVoices()
        except:
            pass



        # 強制 4/4

        for measure in part.getElementsByClass(
            stream.Measure
        ):


            measure.timeSignature = meter.TimeSignature(
                "4/4"
            )


            remove=[]


            # ======================
            # 移除異常 offset
            # ======================

            for element in measure.notesAndRests:


                if element.offset < 0:

                    remove.append(element)


                if element.duration.quarterLength <= 0:

                    remove.append(element)



            for element in remove:

                measure.remove(element)



    # ==========================
    # chord 單音化
    # 避免 jianpu_ly octave 錯誤
    # ==========================


    for part in score.parts:


        for measure in part.getElementsByClass(
            stream.Measure
        ):


            replace=[]


            for element in measure.notes:


                if isinstance(
                    element,
                    chord.Chord
                ):


                    # 保留最高音

                    n = element.sortAscending()[0]

                    replace.append(
                        (
                            element,
                            n
                        )
                    )



            for old,new in replace:

                measure.replace(
                    old,
                    new
                )



    # ==========================
    # 重新建立小節
    # ==========================

    for part in score.parts:

        try:

            part.makeMeasures(
                inPlace=True
            )

        except:

            pass



    # ==========================
    # 清除 barline
    # ==========================

    for part in score.parts:

        for measure in part.getElementsByClass(
            stream.Measure
        ):

            measure.leftBarline = None
            measure.rightBarline = None



    # ==========================
    # 輸出
    # ==========================

    score.write(
        "musicxml",
        fp=output_file
    )


    print(
        "clean完成"
    )



if __name__ == "__main__":


    if len(sys.argv) < 3:

        print(
            "使用方式:"
        )

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit()



    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )