import xml.etree.ElementTree as ET
import sys


def clean_musicxml(input_file, output_file):

    print("開始 clean MusicXML")


    tree = ET.parse(input_file)
    root = tree.getroot()


    # namespace
    ns = {
        "m": "http://www.musicxml.org/ns/musicxml"
    }


    # 移除 octave-change
    for elem in root.iter():

        tag = elem.tag.split("}")[-1]

        if tag == "octave-change":
            parent = None

    # 清除所有 octave 元素
    for parent in root.iter():

        remove = []

        for child in list(parent):

            tag = child.tag.split("}")[-1]

            if tag in [
                "octave-change",
                "accidental-text",
                "credit"
            ]:
                remove.append(child)


        for child in remove:
            parent.remove(child)



    # 修正 divisions
    for elem in root.iter():

        tag = elem.tag.split("}")[-1]

        if tag == "divisions":

            try:
                value=int(elem.text)

                if value > 16:
                    elem.text="16"

            except:
                elem.text="16"



    # 移除異常 voice
    for note in root.iter():

        tag=note.tag.split("}")[-1]

        if tag=="voice":

            if note.text not in ["1", "2"]:
                note.text="1"



    # 移除 backup 過大的問題
    for elem in root.iter():

        tag=elem.tag.split("}")[-1]

        if tag=="backup":

            duration=elem.find(".//duration")

            if duration is not None:

                try:
                    if int(duration.text)>64:
                        duration.text="0"

                except:
                    duration.text="0"



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

    else:

        clean_musicxml(
            sys.argv[1],
            sys.argv[2]
        )