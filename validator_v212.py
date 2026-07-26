import xml.etree.ElementTree as ET


def fix_jianpu_xml(input_file, output_file):

    tree = ET.parse(input_file)
    root = tree.getroot()

    ns = {
        "m": "http://www.musicxml.org/ns/musicxml"
    }

    for measure in root.iter():

        if measure.tag.endswith("measure"):

            for attr in list(measure.attrib):
                if attr == "number":
                    continue


    # 修正 time signature
    for time in root.iter():

        if time.tag.endswith("beats"):
            time.text = "4"

        if time.tag.endswith("beat-type"):
            time.text = "4"


    # 移除 jianpu_ly 不接受的特殊時間
    for measure in root.iter():

        if measure.tag.endswith("measure"):

            for child in list(measure):

                if child.tag.endswith("attributes"):

                    for x in list(child):

                        if x.tag.endswith("time"):
                            continue


    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True
    )

    print("VALIDATOR V21.2 DONE")
    print(output_file)