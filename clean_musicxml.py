import xml.etree.ElementTree as ET


def fix_jianpu_xml(filename):

    print("JIANPU VALIDATOR V21.2")

    tree = ET.parse(filename)
    root = tree.getroot()

    fixed = 0

    for elem in root.iter():

        tag = elem.tag.split("}")[-1]

        # 修正 jianpu_ly 不接受的 duration
        if tag == "duration":

            try:
                value = float(elem.text)

                if value == 7.0:
                    print("fix duration 7.0 -> 4")
                    elem.text = "4"
                    fixed += 1

                elif value not in [
                    0.5,
                    0.75,
                    1,
                    1.5,
                    2,
                    3,
                    4,
                    6,
                    8,
                    12
                ]:
                    print(
                        "remove invalid duration:",
                        value
                    )

                    elem.text = "4"
                    fixed += 1

            except:
                pass


        # 移除非法 time modification
        if tag == "time-modification":

            print("remove time-modification")

            parent = None

    tree.write(
        filename,
        encoding="utf-8",
        xml_declaration=True
    )

    print(
        "V21.2 DONE fixed:",
        fixed
    )