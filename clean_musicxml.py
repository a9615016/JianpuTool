import sys
import xml.etree.ElementTree as ET


def clean_musicxml(input_file, output_file):

    print("CLEAN MUSICXML FINAL V10")

    print("input:")
    print(input_file)

    print("output:")
    print(output_file)


    tree = ET.parse(input_file)
    root = tree.getroot()


    # 移除 namespace
    for elem in root.iter():
        if "}" in elem.tag:
            elem.tag = elem.tag.split("}",1)[1]


    print("remove backup forward")

    for parent in root.iter():

        for child in list(parent):

            if child.tag == "backup" or child.tag == "forward":
                parent.remove(child)



    print("remove chords")

    for parent in root.iter():

        for child in list(parent):

            if child.tag == "chord":
                parent.remove(child)



    print("force divisions=16")

    for div in root.findall(".//divisions"):
        div.text="16"



    print("force 4/4")

    for time in root.findall(".//time"):

        for c in list(time):
            time.remove(c)

        beats=ET.SubElement(time,"beats")
        beats.text="4"

        beat=ET.SubElement(time,"beat-type")
        beat.text="4"



    print("keep voice 1")

    for parent in root.iter():

        for note in list(parent):

            if note.tag=="note":

                voice=note.find("voice")

                if voice is not None and voice.text!="1":
                    parent.remove(note)



    print("split long notes")

    # 修正 duration 過長
    for note in root.findall(".//note"):

        duration = note.find("duration")

        if duration is not None:

            try:
                value=int(duration.text)

                # divisions=16
                # 一小節=64
                # 超過64拆短
                if value > 64:

                    print(
                        "split duration:",
                        value
                    )

                    duration.text="64"


            except:
                pass



    print("remove unsupported tags")


    remove=[
        "staff",
        "instrument",
        "sound"
    ]


    for tag in remove:

        for parent in root.iter():

            for child in list(parent):

                if child.tag==tag:
                    parent.remove(child)



    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True
    )


    print("DONE")
    print(output_file)



if __name__=="__main__":

    if len(sys.argv)<3:

        print(
            "python clean_musicxml_final_v10.py input.musicxml output.musicxml"
        )

        sys.exit()


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )