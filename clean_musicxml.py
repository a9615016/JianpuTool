import sys
import xml.etree.ElementTree as ET


def clean_musicxml(input_file, output_file):

    print("CLEAN MUSICXML FINAL V9")

    print("input:")
    print(input_file)

    print("output:")
    print(output_file)


    tree = ET.parse(input_file)
    root = tree.getroot()


    ns = {
        "m": "http://www.musicxml.org/xsd/partwise"
    }


    # namespace
    for elem in root.iter():
        if "}" in elem.tag:
            elem.tag = elem.tag.split("}",1)[1]


    print("remove backup forward")

    for backup in root.findall(".//backup"):
        parent = None
        for p in root.iter():
            if backup in list(p):
                parent = p
                break

        if parent:
            parent.remove(backup)


    print("remove chords")

    for chord in root.findall(".//chord"):
        parent = None
        for p in root.iter():
            if chord in list(p):
                parent = p
                break

        if parent:
            parent.remove(chord)


    print("force 4/4")

    # 強制所有 part 使用 4/4
    for measure in root.findall(".//measure"):

        attrs = measure.findall("attributes")

        for attr in attrs:

            time = attr.find("time")

            if time is not None:

                for child in list(time):
                    time.remove(child)

                beats = ET.SubElement(time,"beats")
                beats.text = "4"

                beat_type = ET.SubElement(time,"beat-type")
                beat_type.text = "4"


    print("fix divisions")

    for div in root.findall(".//divisions"):

        div.text = "16"


    print("keep voice 1")

    for note in root.findall(".//note"):

        voice = note.find("voice")

        if voice is not None:

            if voice.text != "1":

                parent=None

                for p in root.iter():

                    if note in list(p):
                        parent=p
                        break

                if parent:
                    parent.remove(note)


    print("remove unsupported tags")

    remove_tags=[
        "staff",
        "instrument",
        "sound"
    ]

    for tag in remove_tags:

        for item in root.findall(".//"+tag):

            parent=None

            for p in root.iter():

                if item in list(p):
                    parent=p
                    break

            if parent:
                parent.remove(item)



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
            "python clean_musicxml_final_v9.py input.musicxml output.musicxml"
        )

        sys.exit()


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )