import xml.etree.ElementTree as ET
import sys


def clean_musicxml(input_file, output_file):

    print("開始 clean MusicXML")

    tree = ET.parse(input_file)
    root = tree.getroot()


    # -----------------------
    # 移除 pickup / anacrusis
    # -----------------------

    for measure in root.findall(".//measure"):

        for child in list(measure):

            tag = child.tag.replace(
                "{http://www.musicxml.org/ns/musicxml}",
                ""
            )

            if tag == "attributes":

                time = child.find(
                    ".//{*}time"
                )

                if time is not None:

                    beats = time.find(
                        "{*}beats"
                    )

                    beat_type = time.find(
                        "{*}beat-type"
                    )

                    if beats is not None:
                        beats.text = "4"

                    if beat_type is not None:
                        beat_type.text = "4"


        # 移除 pickup 標記
        if "implicit" in measure.attrib:

            del measure.attrib["implicit"]



    # -----------------------
    # divisions 固定
    # -----------------------

    for div in root.findall(".//{*}divisions"):

        div.text = "16"



    # -----------------------
    # duration 限制
    # -----------------------

    for d in root.findall(".//{*}duration"):

        try:

            value=int(d.text)

            if value > 16:
                d.text="16"

            if value <=0:
                d.text="1"

        except:

            d.text="1"



    # -----------------------
    # octave 修正
    # -----------------------

    for o in root.findall(".//{*}octave"):

        try:

            n=int(o.text)

            if n < 1:
                o.text="1"

            elif n > 8:
                o.text="8"

        except:

            o.text="4"



    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True
    )


    print("clean完成")


if __name__=="__main__":

    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )