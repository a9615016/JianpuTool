# jianpu_prepare_v7.py

import sys
import xml.etree.ElementTree as ET


print("######## JIANPU PREPARE V7 ########")


def count_notes(root):
    return len(root.findall(".//note"))


def count_pitch(root):
    return len(root.findall(".//pitch"))


def fix_time_signature(root):

    for time in root.findall(".//time"):

        beats = time.find("beats")
        beat_type = time.find("beat-type")

        if beats is not None:
            beats.text = "4"

        if beat_type is not None:
            beat_type.text = "4"



def fix_measure_attributes(root):

    """
    不改音符
    只確保 measure 有編號
    """

    measures = root.findall(".//measure")

    for i, m in enumerate(measures, start=1):

        if "number" not in m.attrib:
            m.attrib["number"] = str(i)



def process(src, dst):

    tree = ET.parse(src)
    root = tree.getroot()


    print(
        "BEFORE NOTES:",
        count_notes(root)
    )

    print(
        "BEFORE PITCH:",
        count_pitch(root)
    )


    # 只做安全修改

    fix_time_signature(root)

    fix_measure_attributes(root)


    print(
        "AFTER NOTES:",
        count_notes(root)
    )

    print(
        "AFTER PITCH:",
        count_pitch(root)
    )


    tree.write(
        dst,
        encoding="utf-8",
        xml_declaration=True
    )


    print("WRITE:", dst)



if __name__ == "__main__":

    if len(sys.argv) < 3:

        print(
            "python jianpu_prepare_v7.py input.musicxml output.musicxml"
        )

        sys.exit(1)


    process(
        sys.argv[1],
        sys.argv[2]
    )