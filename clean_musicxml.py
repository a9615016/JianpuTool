import xml.etree.ElementTree as ET
import sys
import os


def clean_musicxml(input_file, output_file):

    tree = ET.parse(input_file)
    root = tree.getroot()


    # namespace
    ns = {
        "m": "http://www.musicxml.org/dtds/partwise.dtd"
    }


    # 移除 grace note
    for elem in root.findall(".//{*}grace"):
        parent = None
        for p in root.iter():
            if elem in list(p):
                parent = p
                break
        if parent is not None:
            parent.remove(elem)


    # 移除 tie
    for elem in root.findall(".//{*}tie"):
        parent = None
        for p in root.iter():
            if elem in list(p):
                parent = p
                break
        if parent is not None:
            parent.remove(elem)


    # 修正 duration
    for duration in root.findall(".//{*}duration"):

        try:
            value = int(duration.text)

            if value <= 0:
                duration.text="1"

        except:
            duration.text="1"



    # 移除不支援的 ornament
    remove_tags=[
        "ornaments",
        "technical",
        "articulations"
    ]


    for tag in remove_tags:

        for elem in root.findall(".//{*}"+tag):

            parent=None

            for p in root.iter():

                if elem in list(p):
                    parent=p
                    break

            if parent:
                parent.remove(elem)



    # 修正 divisions

    for div in root.findall(".//{*}divisions"):

        try:

            v=int(div.text)

            if v>16:
                div.text="16"

        except:
            div.text="16"



    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True
    )


    print("clean完成")


if __name__=="__main__":

    if len(sys.argv)<3:

        print(
        "python clean_musicxml.py input.musicxml output.musicxml"
        )

        exit()


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )