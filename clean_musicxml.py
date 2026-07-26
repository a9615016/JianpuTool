import sys
import os
import xml.etree.ElementTree as ET


VERSION = "CLEAN VERSION 20260726 V21.1"


def clean_musicxml(input_file, output_file):

    print(VERSION)
    print("input:", input_file)

    tree = ET.parse(input_file)
    root = tree.getroot()


    # namespace
    ns = ""

    if root.tag.startswith("{"):
        ns = root.tag.split("}")[0] + "}"


    print("remove voices")


    # remove voice tags
    for elem in root.iter():

        for child in list(elem):

            if child.tag == ns + "voice":
                elem.remove(child)



    print("remove chords")


    # remove chord tags
    for elem in root.iter():

        for child in list(elem):

            if child.tag == ns + "chord":
                elem.remove(child)



    print("remove grace")


    # remove grace notes
    for elem in root.iter():

        for child in list(elem):

            if child.tag == ns + "grace":
                elem.remove(child)



    print("force 4/4")


    # 強制 4/4
    for time in root.iter(ns + "time"):

        for child in list(time):

            if child.tag == ns + "beats":
                child.text = "4"

            if child.tag == ns + "beat-type":
                child.text = "4"



    print("fix measure duration V21.1")


    divisions = 1


    # 取得 divisions
    for d in root.iter(ns + "divisions"):

        try:
            divisions = int(d.text)
        except:
            divisions = 1



    # 修 duration
    for note in root.iter(ns + "note"):

        for duration in note.iter(ns + "duration"):

            try:

                value = float(duration.text)

                # 過大 duration 修正
                if value > divisions * 8:

                    print(
                        "fix duration:",
                        value,
                        "->",
                        divisions
                    )

                    duration.text = str(divisions)


            except:
                pass



    print("remove invalid time")


    # 移除 jianpu_ly 不支援的 measure-style
    for elem in root.iter():

        for child in list(elem):

            if child.tag.endswith("measure-style"):

                elem.remove(child)



    # 移除非法 time-modification
    for elem in root.iter():

        for child in list(elem):

            if child.tag.endswith("time-modification"):

                elem.remove(child)



    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True
    )


    print("V21.1 DONE:")
    print(output_file)



if __name__ == "__main__":


    if len(sys.argv) < 2:

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )
        sys.exit()



    input_file = sys.argv[1]


    if len(sys.argv) >= 3:
        output_file = sys.argv[2]

    else:
        base = os.path.splitext(input_file)[0]
        output_file = base + "_clean.musicxml"



    clean_musicxml(
        input_file,
        output_file
    )