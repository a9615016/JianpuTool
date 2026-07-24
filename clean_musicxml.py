import sys
from music21 import converter
from music21 import meter
from music21 import note
from music21 import stream


def clean_musicxml(input_file, output_file):

    print("開始清理 MusicXML")

    print("輸入:", input_file)


    score = converter.parse(input_file)


    # ==========================
    # 強制 4/4
    # ==========================

    for part in score.parts:

        for measure in part.getElementsByClass("Measure"):

            ts = measure.timeSignature

            if ts is None:

                measure.insert(
                    0,
                    meter.TimeSignature("4/4")
                )



    # ==========================
    # 移除異常音符
    # ==========================

    for part in score.parts:

        for measure in part.getElementsByClass("Measure"):


            remove_list = []


            for element in measure.notesAndRests:


                # 移除負 duration

                if element.duration.quarterLength < 0:

                    remove_list.append(element)



            for item in remove_list:

                measure.remove(item)



    # ==========================
    # 修正 voice
    # ==========================

    for part in score.parts:

        for measure in part.getElementsByClass("Measure"):


            for element in measure:

                if isinstance(element, note.Note):

                    element.voice = None



    # ==========================
    # 移除空 voice
    # ==========================

    for part in score.parts:

        for measure in part.getElementsByClass("Measure"):

            voices = measure.getElementsByClass(
                stream.Voice
            )

            for v in voices:

                if len(v.notesAndRests)==0:

                    measure.remove(v)



    # ==========================
    # 輸出
    # ==========================

    score.write(
        "musicxml",
        fp=output_file
    )


    print(
        "清理完成:",
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

        sys.exit()



    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )