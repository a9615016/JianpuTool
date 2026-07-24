import xml.etree.ElementTree as ET
import sys


def clean_musicxml(input_file, output_file):

    tree = ET.parse(input_file)

    root = tree.getroot()


    # namespace
    ns = "{http://www.musicxml.org/ns/musicxml}"


    # ======================
    # 移除 chord
    # ======================

    for measure in root.iter(ns + "measure"):

        notes = list(measure)

        remove_next = False

        for item in notes:

            if item.tag == ns + "note":

                if item.find(ns + "chord") is not None:

                    measure.remove(item)



    # ======================
    # 移除 backup
    # ======================

    for backup in root.iter(ns + "backup"):

        for parent in root.iter():

            if backup in list(parent):

                parent.remove(backup)

                break



    # ======================
    # 只保留 voice 1
    # ======================

    for note in root.iter(ns + "note"):

        voice = note.find(ns + "voice")

        if voice is not None:

            if voice.text != "1":

                for parent in root.iter():

                    if note in list(parent):

                        parent.remove(note)

                        break



    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True
    )



if __name__ == "__main__":

    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )