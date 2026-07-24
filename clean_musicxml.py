import xml.etree.ElementTree as ET
import sys


def clean_musicxml(input_file, output_file):

    tree = ET.parse(input_file)
    root = tree.getroot()

    ns = "{http://www.musicxml.org/ns/musicxml}"


    # ==========================
    # 移除所有 chord 音符
    # 保留第一個音
    # ==========================

    for measure in root.iter(ns + "measure"):

        notes = list(measure)

        first_note = True


        for item in notes:

            if item.tag == ns + "note":

                chord = item.find(ns + "chord")


                if chord is not None:

                    # 刪除和弦後續音
                    measure.remove(item)



    # ==========================
    # 移除 backup
    # ==========================

    for parent in root.iter():

        for child in list(parent):

            if child.tag == ns + "backup":

                parent.remove(child)



    # ==========================
    # 移除 voice 2以上
    # ==========================

    for parent in root.iter():

        for note in list(parent):

            if note.tag == ns + "note":

                voice = note.find(ns + "voice")


                if voice is not None:

                    if voice.text != "1":

                        parent.remove(note)



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

        exit()


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )