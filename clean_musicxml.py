import sys
import xml.etree.ElementTree as ET


def clean_musicxml(input_file, output_file):

    print("開始 clean MusicXML")

    tree = ET.parse(input_file)
    root = tree.getroot()


    # namespace
    ns = {
        "m": "http://www.musicxml.org/ns/musicxml"
    }


    # 移除所有 pickup
    for measure in root.findall(".//m:measure", ns):

        attrs = measure.find("m:attributes", ns)

        if attrs is not None:

            # 改拍號
            time = attrs.find("m:time", ns)

            if time is not None:

                beats = time.find("m:beats", ns)
                beat_type = time.find("m:beat-type", ns)

                if beats is not None:
                    beats.text = "4"

                if beat_type is not None:
                    beat_type.text = "4"


        # 移除 pickup 標記
        for elem in measure.findall(".//m:forward", ns):
            measure.remove(elem)


    # 修正 encoding
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
        exit()


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )