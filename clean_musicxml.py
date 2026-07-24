import xml.etree.ElementTree as ET
import sys


def clean_musicxml(input_file, output_file):

    tree = ET.parse(input_file)
    root = tree.getroot()

    ns = {
        "m": "http://www.musicxml.org/ns/musicxml",
        "": "http://www.musicxml.org/ns/musicxml"
    }

    # 移除非法 octave
    for note in root.iter():

        tag = note.tag.split("}")[-1]

        if tag == "octave":
            try:
                value = int(note.text)

                if value < 0 or value > 8:
                    note.text = "4"

            except:
                note.text = "4"


    # 修正 step
    for step in root.iter():

        tag = step.tag.split("}")[-1]

        if tag == "step":

            if step.text not in [
                "A","B","C","D","E","F","G"
            ]:
                step.text = "C"


    # 移除多餘 voice
    for note in root.iter():

        tag = note.tag.split("}")[-1]

        if tag == "voice":

            if note.text:
                if note.text not in ["1","2"]:
                    note.text="1"


    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True
    )


if __name__ == "__main__":

    if len(sys.argv)<3:
        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )
        exit()


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )

    print("clean完成")