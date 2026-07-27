import sys
import os
import xml.etree.ElementTree as ET
from fractions import Fraction


def clean_musicxml(input_file, output_file):

    print("CLEAN MUSICXML")

    tree = ET.parse(input_file)
    root = tree.getroot()

    ns = {
        "m": "http://www.musicxml.org/ns/musicxml"
    }


    # 找 divisions
    divisions = 1

    div_node = root.find(
        ".//m:divisions",
        ns
    )

    if div_node is not None:
        divisions = int(div_node.text)


    print("divisions =", divisions)



    # 強制移除容易造成 jianpu_ly 失敗的元素

    remove_tags = [
        "backup",
        "forward",
        "grace",
        "chord"
    ]


    for tag in remove_tags:

        for node in root.findall(
            ".//m:" + tag,
            ns
        ):
            parent = None

            for p in root.iter():

                if node in list(p):
                    parent = p
                    break


            if parent is not None:
                parent.remove(node)



    # 修正每小節 duration

    measures = root.findall(
        ".//m:measure",
        ns
    )


    print("measures =", len(measures))


    for measure in measures:


        total_duration = 0

        notes = measure.findall(
            "m:note",
            ns
        )


        for note in notes:

            duration = note.find(
                "m:duration",
                ns
            )


            if duration is not None:

                total_duration += int(
                    duration.text
                )


        # 4/4 小節應該 = divisions*4

        target = divisions * 4


        if total_duration > target:

            print(
                "修正超長小節:",
                measure.attrib.get("number"),
                total_duration,
                "->",
                target
            )


            overflow = total_duration - target


            for note in reversed(notes):

                duration = note.find(
                    "m:duration",
                    ns
                )

                if duration is None:
                    continue


                d = int(duration.text)


                if overflow <= 0:
                    break


                if d <= overflow:

                    overflow -= d
                    measure.remove(note)


                else:

                    duration.text = str(
                        d-overflow
                    )

                    overflow = 0



    # 加入簡單標題

    print("write")

    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True
    )


    print(
        "DONE",
        output_file
    )



if __name__ == "__main__":


    if len(sys.argv) < 3:

        print(
            "usage: python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit(1)


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )