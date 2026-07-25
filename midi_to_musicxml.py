import os
import sys
import music21


def midi_to_musicxml(input_file, output_file=None):

    print("開始 MIDI → MusicXML")
    print("輸入:", input_file)


    if not os.path.exists(input_file):
        raise FileNotFoundError(
            input_file
        )


    # 沒指定輸出就自動產生
    if output_file is None:

        base = os.path.splitext(
            input_file
        )[0]

        output_file = base + ".musicxml"



    print("讀取 MIDI...")


    score = music21.converter.parse(
        input_file
    )


    print("寫入 MusicXML...")


    score.write(
        "musicxml",
        fp=output_file
    )


    print("完成:")
    print(output_file)


    return output_file




if __name__ == "__main__":


    if len(sys.argv) < 2:

        print(
            "使用方式:"
        )

        print(
            "python midi_to_musicxml.py input.mid output.musicxml"
        )

        sys.exit(1)



    midi_file = sys.argv[1]


    if len(sys.argv) >= 3:

        output_file = sys.argv[2]

    else:

        output_file = None



    midi_to_musicxml(
        midi_file,
        output_file
    )