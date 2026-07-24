import xml.etree.ElementTree as ET
import sys


def clean_musicxml(input_file, output_file):

    tree = ET.parse(input_file)

    root = tree.getroot()


    namespace = {
        "m":"http://www.musicxml.org/ns/musicxml"
    }


    # 移除 voice 2 以上

    for note in root.findall(".//note"):

        voice = note.find("voice")

        if voice is not None:

            if voice.text != "1":

                parent = None

                for p in root.iter():

                    if note in list(p):

                        parent = p
                        break


                if parent is not None:

                    parent.remove(note)



    # 移除 chord 標記

    for note in root.findall(".//note"):

        chord = note.find("chord")

        if chord is not None:

            note.remove(chord)



    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True
    )



if __name__=="__main__":


    if len(sys.argv)<3:

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        exit()



    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )