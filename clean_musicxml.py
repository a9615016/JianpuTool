import sys
import xml.etree.ElementTree as ET


def clean_musicxml(input_file, output_file):

    print("開始 clean MusicXML")
    print("輸入:", input_file)

    tree = ET.parse(input_file)
    root = tree.getroot()


    # MusicXML namespace
    ns = {
        "m": "http://www.musicxml.org/ns/musicxml"
    }


    # 修正 duration 異常
    for duration in root.iter("duration"):
        try:
            value = int(duration.text)

            if value <= 0:
                duration.text = "1"

        except:
            duration.text = "1"



    # 移除 grace
    for grace in root.iter("grace"):
        parent = None

    for note in root.iter("note"):

        # 移除不完整 octave
        pitch = note.find("pitch")

        if pitch is not None:

            octave = pitch.find("octave")

            if octave is not None:

                try:
                    o = int(octave.text)

                    # jianpu_ly 支援範圍
                    if o < 1:
                        octave.text = "1"

                    if o > 8:
                        octave.text = "8"

                except:
                    octave.text = "4"



    # 修正 time signature
    for beats in root.iter("beats"):

        if beats.text not in [
            "2",
            "3",
            "4",
            "6"
        ]:
            beats.text = "4"


    for beat_type in root.iter("beat-type"):

        if beat_type.text not in [
            "2",
            "4",
            "8"
        ]:
            beat_type.text = "4"



    # 移除空 voice
    for voice in root.iter("voice"):

        if voice.text is None:
            voice.text = "1"



    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True
    )


    print("clean完成")
    print("輸出:", output_file)



if __name__ == "__main__":

    if len(sys.argv) < 3:

        print(
            "使用方式:\n"
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        exit()


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )