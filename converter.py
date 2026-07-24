import os
import sys
import music21


def midi_to_musicxml(input_file):

    print("開始 MIDI → MusicXML")
    print("輸入:", input_file)


    if not os.path.exists(input_file):
        raise Exception(
            "找不到 MIDI: " + input_file
        )


    folder = os.path.dirname(input_file)

    output_file = os.path.join(
        folder,
        "input.musicxml"
    )


    print("輸出:", output_file)


    # ==========================
    # 讀取 MIDI
    # ==========================

    score = music21.converter.parse(
        input_file
    )


    print("MIDI讀取完成")



    # ==========================
    # 只保留第一聲部
    # (避免鋼琴左右手干擾)
    # ==========================

    try:

        part = score.parts[0]

        score = music21.stream.Score()

        score.append(part)

        print("保留第一聲部")

    except Exception:

        print("無法分離聲部，使用原資料")



    # ==========================
    # 節奏量化
    # ==========================

    print("開始量化")


    for part in score.parts:


        part.quantize(
            quarterLengthDivisors=[
                1,
                2,
                4
            ],

            processOffsets=True,

            processDurations=True
        )


    print("量化完成")



    # ==========================
    # 建立小節
    # ==========================

    for part in score.parts:

        part.makeMeasures(
            inPlace=True
        )


    print("小節建立完成")



    # ==========================
    # 移除過短音符
    # ==========================

    remove_list = []


    for part in score.parts:

        for n in part.recurse().notes:

            if n.duration.quarterLength < 0.25:

                remove_list.append(n)



    for n in remove_list:

        n.activeSite.remove(
            n
        )


    print(
        "移除過短音符:",
        len(remove_list)
    )



    # ==========================
    # 輸出 MusicXML
    # ==========================

    score.write(
        "musicxml",
        fp=output_file
    )


    print("MusicXML完成")
    print(output_file)


    return output_file





if __name__ == "__main__":


    if len(sys.argv) < 2:

        print(
            "使用方式:"
        )

        print(
            "python converter.py input.mid"
        )

        sys.exit(1)



    midi_file = sys.argv[1]


    midi_to_musicxml(
        midi_file
    )