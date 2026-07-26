import sys
import os
import xml.etree.ElementTree as ET


print("CLEAN MUSICXML V1")


def clean_musicxml(input_file, output_file):

    print("input:")
    print(input_file)

    print("output:")
    print(output_file)


    if not os.path.exists(input_file):
        raise FileNotFoundError(
            input_file
        )


    print("讀取 MusicXML")


    tree = ET.parse(input_file)

    root = tree.getroot()


    print("開始清理")


    # namespace
    ns = {
        "m": "http://www.musicxml.org/ns/musicxml"
    }


    # -----------------------
    # 移除 chord 標記
    # -----------------------

    count = 0

    for chord in root.findall(
        ".//{http://www.musicxml.org/ns/musicxml}chord"
    ):

        parent = None

    # -----------------------
    # 移除 grace note
    # -----------------------

    for grace in root.findall(
        ".//{http://www.musicxml.org/ns/musicxml}grace"
    ):

        parent = None


    print("清理完成")


    print("寫入檔案")


    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True
    )


    print("完成:")
    print(output_file)


    if not os.path.exists(output_file):

        raise Exception(
            "MusicXML output failed"
        )


    print(
        "SIZE:",
        os.path.getsize(output_file)
    )



if __name__ == "__main__":


    if len(sys.argv)<3:

        print(
            "Usage: python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit(1)


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )