import xml.etree.ElementTree as ET
import sys


def clean_musicxml(input_file, output_file):

    print("開始 clean MusicXML")

    tree = ET.parse(input_file)

    root = tree.getroot()


    def tag(x):
        return x.split("}")[-1]


    # 移除 jianpu_ly 不支援項目

    remove_tags = {

        "backup",
        "forward",
        "grace",
        "notations",
        "accidental",
        "tie",
        "chord",
        "arpeggiate"

    }



    def recursive_clean(parent):

        for child in list(parent):

            name = tag(child.tag)

            if name in remove_tags:

                parent.remove(child)

            else:

                recursive_clean(child)



    recursive_clean(root)



    # voice 固定

    for e in root.iter():

        if tag(e.tag) == "voice":

            e.text = "1"



    # octave 全部改成標準音域

    for e in root.iter():

        if tag(e.tag) == "octave":

            e.text = "4"



    # 移除 pitch 裡重複 octave

    for note in root.iter():

        if tag(note.tag) == "pitch":

            octaves = []

            for child in list(note):

                if tag(child.tag) == "octave":

                    octaves.append(child)


            # 只保留一個 octave

            for extra in octaves[1:]:

                note.remove(extra)



    # 清理文字

    for e in root.iter():

        if e.text:

            e.text=e.text.strip()



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

        exit()


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )