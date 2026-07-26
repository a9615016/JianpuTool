import os
import xml.etree.ElementTree as ET


def fix_jianpu_xml(input_file, output_file):

    print("MusicXML Validator V21.2.1")

    if not os.path.exists(input_file):
        raise FileNotFoundError(
            f"找不到 MusicXML: {input_file}"
        )

    tree = ET.parse(input_file)
    root = tree.getroot()


    # 移除非法 measure-style
    for elem in root.iter():
        if elem.tag.endswith("measure-style"):
            parent = None


    # 修正 time-modification
    for tm in root.iter():
        if tm.tag.endswith("time-modification"):

            actual = tm.find("./{*}actual-notes")
            normal = tm.find("./{*}normal-notes")

            if actual is not None and normal is not None:
                try:
                    a = int(actual.text)
                    n = int(normal.text)

                    if a > 16 or n > 16:
                        tm.clear()

                except:
                    tm.clear()


    # 修正 duration 異常
    for note in root.iter():

        if note.tag.endswith("duration"):

            try:
                value = float(note.text)

                if value < 0:
                    note.text = "0"

            except:
                note.text = "0"


    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True
    )


    print("Validator V21.2.1 DONE:")
    print(output_file)