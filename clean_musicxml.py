import xml.etree.ElementTree as ET
import sys
import os


NS = {
    "m": "http://www.musicxml.org/ns/musicxml"
}

ET.register_namespace("", NS["m"])


def clean_musicxml(input_file, output_file):

    print("開始 clean MusicXML")

    tree = ET.parse(input_file)
    root = tree.getroot()


    # ==========================
    # 移除不需要資訊
    # ==========================

    for elem in root.findall(".//m:credit", NS):
        parent = root
        parent.remove(elem)


    # ==========================
    # 修正 measure
    # ==========================

    for part in root.findall(".//m:part", NS):

        divisions = 1

        attr = part.find(".//m:divisions", NS)

        if attr is not None:
            divisions = int(attr.text)


        # 4/4 = divisions * 4
        target_duration = divisions * 4


        for measure in part.findall("m:measure", NS):

            total = 0


            for note in measure.findall("m:note", NS):

                duration = note.find(
                    "m:duration",
                    NS
                )

                if duration is not None:

                    try:
                        total += int(duration.text)

                    except:
                        pass



            # ==========================
            # 修正短小節
            # ==========================

            if total != target_duration:

                print(
                    "fix measure:",
                    measure.attrib.get("number"),
                    total,
                    "->",
                    target_duration
                )


                diff = target_duration - total


                if diff > 0:

                    note = ET.Element(
                        "{%s}note" % NS["m"]
                    )


                    ET.SubElement(
                        note,
                        "{%s}rest" % NS["m"]
                    )


                    duration = ET.SubElement(
                        note,
                        "{%s}duration" % NS["m"]
                    )

                    duration.text = str(diff)


                    voice = ET.SubElement(
                        note,
                        "{%s}voice" % NS["m"]
                    )

                    voice.text = "1"


                    measure.append(note)



    # ==========================
    # 修正 octave mark 問題
    # 清掉重複 chord note
    # ==========================

    for chord in root.findall(".//m:chord", NS):

        parent = None


    # ==========================
    # 移除空 voice
    # ==========================

    for voice in root.findall(".//m:voice", NS):

        if voice.text is None:

            voice.text = "1"



    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True
    )


    print("clean完成")
    print(output_file)



if __name__ == "__main__":

    if len(sys.argv) < 3:

        print(
            "使用方式:\n"
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit()


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )