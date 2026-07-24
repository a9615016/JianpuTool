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


    # 保留原資料夾
    folder = os.path.dirname(input_file)

    output_file = os.path.join(
        folder,
        "input.musicxml"
    )


    print("輸出:", output_file)


    score = music21.converter.parse(
        input_file
    )


    score.write(
        "musicxml",
        fp=output_file
    )


    print("完成")
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