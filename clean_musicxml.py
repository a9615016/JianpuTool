import xml.etree.ElementTree as ET
import sys
import os


NS = {
    "m": "http://www.musicxml.org/ns/musicxml",
}

ET.register_namespace("", NS["m"])


def clean_musicxml(input_file, output_file):

    tree = ET.parse(input_file)
    root = tree.getroot()


    # ==========================
    # divisions 強制 16
    # ==========================
    for div in root.findall(".//m:divisions", NS):
        div.text = "16"


    # ==========================
    # 移除 grace note
    # ==========================
    for note in root.findall(".//m:note", NS):

        grace = note.find("m:grace", NS)

        if grace is not None:
            parent = None

            for p in root.iter():
                for child in list(p):
                    if child is note:
                        parent = p

            if parent is not None:
                parent.remove(note)



    # ==========================
    # 移除 voice 2+
    # 保留主旋律
    # ==========================

    for voice in root.findall(".//m:voice", NS):

        if voice.text and voice.text.strip() != "1":

            parent=None

            for p in root.iter():
                for child in list(p):
                    if child.tag == voice.tag:
                        if child.text==voice.text:
                            parent=p


            if parent:

                note=None

                for n in parent.findall("m:note",NS):
                    v=n.find("m:voice",NS)

                    if v is not None and v.text!="1":
                        parent.remove(n)



    # ==========================
    # 修正 pickup measure
    # ==========================

    for measure in root.findall(".//m:measure",NS):

        notes=[]

        total=0


        for note in measure.findall("m:note",NS):

            dur=note.find("m:duration",NS)

            if dur is not None:

                try:
                    total += int(dur.text)
                except:
                    pass


        # 4/4 = 64 ticks
        # 太短的小節補休止

        if total < 64:

            rest=ET.Element(
                "{%s}note"%NS["m"]
            )

            ET.SubElement(
                rest,
                "{%s}rest"%NS["m"]
            )

            dur=ET.SubElement(
                rest,
                "{%s}duration"%NS["m"]
            )

            dur.text=str(64-total)


            measure.append(rest)



        # 太長砍掉 pickup 問題

        if total > 128:

            print(
                "remove abnormal measure",
                measure.attrib
            )



    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True
    )


if __name__=="__main__":

    if len(sys.argv)<3:
        print(
        "python clean_musicxml.py input.musicxml output.musicxml"
        )
        sys.exit()


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )

    print("clean完成")
    print(sys.argv[2])