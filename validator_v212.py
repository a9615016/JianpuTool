import xml.etree.ElementTree as ET


def fix_jianpu_xml(input_file, output_file):

    tree = ET.parse(input_file)
    root = tree.getroot()

    namespace = {
        "m": "http://www.musicxml.org"
    }

    # 修正非法 measure-style
    for elem in root.iter():

        tag = elem.tag.split("}")[-1]

        if tag == "beats":

            if elem.text:
                try:
                    value = float(elem.text)

                    # jianpu_ly 不接受奇怪拍號
                    if value <= 0:
                        elem.text = "4"

                except:
                    elem.text = "4"


        if tag == "beat-type":

            if elem.text:
                try:
                    value = float(elem.text)

                    if value not in [1,2,4,8,16]:
                        elem.text = "4"

                except:
                    elem.text="4"


    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True
    )

    print("validator V21.2 DONE")
    print(output_file)