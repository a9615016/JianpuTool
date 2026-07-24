import sys
import xml.etree.ElementTree as ET


def clean_musicxml(input_file, output_file):

    print("開始 clean MusicXML")


    tree = ET.parse(input_file)
    root = tree.getroot()


    ns = "{http://www.musicxml.org/ns/musicxml}"


    # 1. 強制刪除 pickup 標記
    for measure in root.findall(".//" + ns + "measure"):

        if measure.attrib.get("implicit") == "yes":
            measure.attrib.pop("implicit")


    # 2. 第一小節移除 forward / backup
    measures = root.findall(".//" + ns + "measure")

    if len(measures) > 0:

        first = measures[0]

        for x in list(first):

            if x.tag in [
                ns+"forward",
                ns+"backup"
            ]:
                first.remove(x)



    # 3. 所有拍號固定 4/4

    for time in root.findall(".//"+ns+"time"):

        beats = time.find(ns+"beats")
        beat_type = time.find(ns+"beat-type")

        if beats is not None:
            beats.text="4"

        if beat_type is not None:
            beat_type.text="4"



    # 4. 修正 XML encoding

    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True
    )


    print("clean完成")
    print(output_file)



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