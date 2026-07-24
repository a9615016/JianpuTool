import xml.etree.ElementTree as ET
import sys
import os


def clean_musicxml(input_file, output_file):

    print("開始 clean MusicXML")

    tree = ET.parse(input_file)
    root = tree.getroot()

    ns = ""

    # 移除 backup
    for backup in root.findall(".//backup"):
        parent = None
        for p in root.iter():
            if backup in list(p):
                parent = p
                break

        if parent is not None:
            parent.remove(backup)


    # 修正音符
    for note in root.findall(".//note"):

        # 移除 chord 標記
        for chord in note.findall("chord"):
            note.remove(chord)


        # 修正 octave
        pitch = note.find("pitch")

        if pitch is not None:

            octave = pitch.find("octave")

            if octave is not None:

                try:
                    value = int(octave.text)

                    # 限制合理音域
                    if value < 1:
                        octave.text = "1"

                    if value > 8:
                        octave.text = "8"

                except:
                    octave.text = "4"



        # 移除奇怪 duration
        duration = note.find("duration")

        if duration is not None:

            try:
                d = int(duration.text)

                if d <= 0:
                    duration.text = "16"

            except:
                duration.text = "16"



    # 修正 divisions

    for div in root.findall(".//divisions"):

        try:

            value=int(div.text)

            if value > 32:
                div.text="16"

            if value <=0:
                div.text="16"

        except:

            div.text="16"



    # 修正 time signature

    for beats in root.findall(".//beats"):

        if beats.text not in ["2","3","4","6"]:
            beats.text="4"


    for beat_type in root.findall(".//beat-type"):

        if beat_type.text not in ["2","4","8"]:
            beat_type.text="4"



    # UTF-8輸出
    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True
    )


    print("clean完成")
    print(output_file)



if __name__=="__main__":

    if len(sys.argv)<3:

        print(
        "使用方式:\n"
        "python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit()


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )