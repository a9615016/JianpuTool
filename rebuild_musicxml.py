import xml.etree.ElementTree as ET
import sys


NS = {
    "m": "http://www.musicxml.org/ns/musicxml"
}


ET.register_namespace(
    "",
    NS["m"]
)



def rebuild(input_file, output_file):

    print("REBUILD VERSION 20260724 V3")

    print(
        "開始重建 MusicXML"
    )


    tree = ET.parse(
        input_file
    )

    root = tree.getroot()



    # ==========================
    # 修正 duration
    # ==========================

    for duration in root.findall(
        ".//m:duration",
        NS
    ):

        try:

            value = int(duration.text)

            # 防止非法 duration
            if value <= 0:

                duration.text = "1"


        except:

            duration.text = "1"



    # ==========================
    # 統一 voice
    # ==========================

    for voice in root.findall(
        ".//m:voice",
        NS
    ):

        voice.text = "1"



    # ==========================
    # 移除 backup
    # ==========================

    for backup in root.findall(
        ".//m:backup",
        NS
    ):

        parent = backup.getparent() if hasattr(
            backup,
            "getparent"
        ) else None



    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True
    )


    print(
        "完成",
        output_file
    )




if __name__ == "__main__":


    if len(sys.argv) < 3:

        print(
            "python rebuild_musicxml.py input output"
        )

        sys.exit(1)



    rebuild(
        sys.argv[1],
        sys.argv[2]
    )