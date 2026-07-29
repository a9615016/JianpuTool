# jianpu_prepare_v5.py

import sys
import xml.etree.ElementTree as ET


def count_notes(root):
    return len(root.findall(".//note"))


def fix_musicxml(src, dst):

    tree = ET.parse(src)
    root = tree.getroot()

    before = count_notes(root)

    print("######## JIANPU PREPARE V5 ########")
    print("BEFORE NOTES:", before)


    # namespace
    ns = ""

    # 強制 4/4
    for attr in root.findall(".//time"):
        beats = attr.find("beats")
        beat_type = attr.find("beat-type")

        if beats is not None:
            beats.text = "4"

        if beat_type is not None:
            beat_type.text = "4"


    after = count_notes(root)

    print("AFTER NOTES:", after)


    tree.write(
        dst,
        encoding="utf-8",
        xml_declaration=True
    )

    print("WRITE:", dst)



if __name__ == "__main__":

    if len(sys.argv) < 3:
        print(
            "python jianpu_prepare_v5.py input.musicxml output.musicxml"
        )
        exit()


    fix_musicxml(
        sys.argv[1],
        sys.argv[2]
    )