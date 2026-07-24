import xml.etree.ElementTree as ET
import sys


def clean_musicxml(input_file, output_file):

    print("開始 clean MusicXML")
    print("輸入:", input_file)

    tree = ET.parse(input_file)
    root = tree.getroot()


    # =========================
    # 移除不支援元素
    # =========================

    remove_tags = [
        "grace",
        "ornaments",
        "technical",
        "articulations",
        "fermata",
        "tie"
    ]


    for tag in remove_tags:

        for elem in root.findall(".//{*}" + tag):

            parent = None

            for p in root.iter():

                if elem in list(p):
                    parent = p
                    break

            if parent is not None:
                parent.remove(elem)



    # =========================
    # 強制拍號 4/4
    # 解決 jianpu_ly KeyError 16
    # =========================

    for time in root.findall(".//{*}time"):

        beats = time.find("{*}beats")
        beat_type = time.find("{*}beat-type")


        if beats is not None:
            beats.text = "4"


        if beat_type is not None:
            beat_type.text = "4"



    # =========================
    # divisions 修正
    # =========================

    for div in root.findall(".//{*}divisions"):

        try:

            value = int(div.text)

            if value != 16:
                div.text = "16"

        except:

            div.text = "16"



    # =========================
    # duration 修正
    # =========================

    for duration in root.findall(".//{*}duration"):

        try:

            value = int(duration.text)

            if value <= 0:
                duration.text = "1"


        except:

            duration.text = "1"



    # =========================
    # 移除八度標記問題
    # =========================

    for octave in root.findall(".//{*}octave"):

        parent = None

        for p in root.iter():

            if octave in list(p):

                parent = p
                break


        if parent is not None:
            parent.remove(octave)



    # =========================
    # 輸出
    # =========================

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
            "使用方式:"
            "\npython clean_musicxml.py input.musicxml output.musicxml"
        )

        exit()


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )