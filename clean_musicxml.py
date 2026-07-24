import xml.etree.ElementTree as ET
import sys


def clean_musicxml(input_file, output_file):

    tree = ET.parse(input_file)

    root = tree.getroot()


    ns = {
        "m": "http://www.musicxml.org/ns/musicxml"
    }


    # 移除 chord 標記
    for chord in root.findall(".//{*}chord"):

        parent = None

        for p in root.iter():

            if chord in list(p):
                parent = p
                break


        if parent is not None:

            parent.remove(chord)



    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True
    )



if __name__ == "__main__":

    if len(sys.argv) < 3:

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit(1)


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )