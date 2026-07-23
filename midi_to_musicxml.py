import os
import music21


def midi_to_musicxml(input_file):

    print("開始 MIDI → MusicXML")
    print("輸入:", input_file)


    # 產生輸出檔名
    base = os.path.splitext(input_file)[0]
    output_file = base + ".musicxml"


    # 讀取 MIDI
    score = music21.converter.parse(
        input_file
    )


    # 輸出 MusicXML
    score.write(
        "musicxml",
        fp=output_file
    )


    print("完成:")
    print(output_file)


    return output_file


# 測試用
if __name__ == "__main__":

    midi_file = "test.mid"

    midi_to_musicxml(
        midi_file
    )