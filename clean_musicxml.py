import sys
from music21 import converter
from music21 import stream
from music21 import meter
from music21 import chord


def clean_musicxml(input_file, output_file):

    print("開始 MusicXML 清理")


    score = converter.parse(input_file)



    for part in score.parts:


        # 移除 voice

        try:
            part.flattenUnnecessaryVoices()
        except:
            pass



        # 重新建立 4/4 小節

        try:

            part.makeMeasures(
                meterStream=meter.TimeSignature("4/4"),
                inPlace=True
            )

        except Exception:

            pass



        for measure in part.getElementsByClass(
            stream.Measure
        ):


            measure.timeSignature = meter.TimeSignature(
                "4/4"
            )


            # =====================
            # 移除 chord
            # =====================

            replace=[]


            for element in measure.notes:


                if isinstance(
                    element,
                    chord.Chord
                ):

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



            # =====================
            # 移除異常 duration
            # =====================

            remove=[]


            for e in measure.notesAndRests:


                if e.duration.quarterLength <=0:

                    remove.append(e)


                if e.offset <0:

                    remove.append(e)



            for e in remove:

                measure.remove(e)



    score.write(
        "musicxml",
        fp=output_file
    )


    print(
        "clean完成"
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