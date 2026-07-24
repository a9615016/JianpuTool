import os
import xml.etree.ElementTree as ET
import music21


def midi_to_musicxml(input_file, output_file=None):

    print("開始 MIDI -> MusicXML")
    print("輸入:", input_file)


    if output_file is None:
        base = os.path.splitext(input_file)[0]
        output_file = base + ".musicxml"


    # MIDI 讀取
    score = music21.converter.parse(input_file)


    # 移除複雜資訊
    for part in score.parts:

        for element in part.recurse():

            # 不要複音
            if element.classes[0] == "Chord":
                element = element.notes[0]


    # 產生 MusicXML
    score.write(
        "musicxml",
        fp=output_file
    )


    print("產生:")
    print(output_file)


    clean_musicxml(output_file)


    return output_file





def clean_musicxml(filename):

    print("開始 clean MusicXML")


    tree = ET.parse(filename)

    root = tree.getroot()


    def tag_name(tag):
        return tag.split("}")[-1]



    # 刪除 jianpu_ly 不支援元素

    remove_tags = {

        "backup",
        "forward",
        "grace",
        "notations",
        "accidental",
        "tie",
        "chord",
        "arpeggiate",
        "technical",
        "ornaments"

    }



    def clean_node(parent):

        for child in list(parent):

            tag = tag_name(child.tag)


            if tag in remove_tags:

                parent.remove(child)

            else:

                clean_node(child)



    clean_node(root)



    # voice 全部改 1

    for elem in root.iter():

        if tag_name(elem.tag) == "voice":

            elem.text = "1"



    # octave 修正

    for elem in root.iter():

        if tag_name(elem.tag) == "octave":

            try:

                octave = int(elem.text)


                if octave < 3:

                    elem.text = "4"


                elif octave > 6:

                    elem.text = "5"


            except:

                elem.text = "4"



    # 移除多餘空白

    for elem in root.iter():

        if elem.text:

            elem.text = elem.text.strip()



    tree.write(
        filename,
        encoding="utf-8",
        xml_declaration=True
    )


    print("clean完成")




if __name__ == "__main__":


    import sys


    if len(sys.argv) < 2:

        print(
            "使用方式:"
            "\npython converter.py input.mid"
        )

        exit()



    midi_to_musicxml(sys.argv[1])