import sys
import os
import xml.etree.ElementTree as ET


NS = {
    "m": "http://www.musicxml.org/ns/musicxml"
}


def remove_namespace(root):
    for elem in root.iter():
        if "}" in elem.tag:
            elem.tag = elem.tag.split("}", 1)[1]


def remove_voices(root):

    print("remove voices")

    for elem in root.iter("voice"):
        elem.text = "1"


def remove_chords(root):

    print("remove chords")

    for note in root.iter("note"):

        for child in list(note):

            if child.tag == "chord":
                note.remove(child)


def remove_grace(root):

    print("remove grace")

    for note in root.iter("note"):

        for child in list(note):

            if child.tag == "grace":
                note.remove(child)


def fix_duration(root):

    print("fix duration")

    mapping = {

        "128th": "16th",
        "64th": "16th",
        "32nd": "16th"

    }

    for elem in root.iter("type"):

        if elem.text in mapping:

            print(
                "duration:",
                elem.text,
                "->",
                mapping[elem.text]
            )

            elem.text = mapping[elem.text]


def remove_tuplets(root):

    print("remove tuplets")

    for elem in list(root.iter("time-modification")):

        parent = None

        for p in root.iter():

            if elem in list(p):
                parent = p
                break

        if parent:
            parent.remove(elem)


def rebuild_measures(root):

    print("rebuild measures")

    measures = root.findall(".//measure")

    for m in measures:

        for note in m.findall("note"):

            duration = note.find("duration")

            if duration is not None:

                try:

                    value = int(duration.text)

                    # 最低音符長
                    if value < 1:
                        duration.text = "1"

                except:

                    pass



def fix_bars(root):

    print("fix bars")

    for measure in root.iter("measure"):

        duration_sum = 0

        for d in measure.iter("duration"):

            try:
                duration_sum += int(d.text)
            except:
                pass


        # 防止超拍
        if duration_sum > 64:

            print(
                "compress measure:",
                measure.attrib.get("number"),
                duration_sum
            )

            extra = duration_sum - 64

            for d in measure.iter("duration"):

                try:

                    value = int(d.text)

                    if value > extra:

                        d.text = str(value-extra)
                        break

                except:
                    pass



def final_cleanup(root):

    print("final cleanup")

    # 移除空標籤

    for parent in root.iter():

        for child in list(parent):

            if child.text is None and len(child)==0:

                parent.remove(child)



def clean_musicxml(input_file, output_file):

    print("CLEAN VERSION 20260726 V7 FINAL")

    print("input:", input_file)


    tree = ET.parse(input_file)

    root = tree.getroot()


    remove_namespace(root)


    remove_voices(root)

    remove_chords(root)

    remove_grace(root)

    fix_duration(root)

    remove_tuplets(root)

    rebuild_measures(root)

    fix_bars(root)

    final_cleanup(root)



    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True
    )


    print("write")

    print("done:", output_file)



if __name__ == "__main__":

    if len(sys.argv) < 2:

        print(
            "python clean_musicxml.py input.musicxml [output.musicxml]"
        )

        sys.exit()


    input_file = sys.argv[1]


    if len(sys.argv)>=3:

        output_file=sys.argv[2]

    else:

        base=os.path.splitext(input_file)[0]

        output_file=base+"_clean.musicxml"



    clean_musicxml(
        input_file,
        output_file
    )