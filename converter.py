import os
import xml.etree.ElementTree as ET
import music21



def midi_to_musicxml(input_file, output_file=None):

    print("開始 MIDI -> MusicXML")
    print("輸入:", input_file)


    if output_file is None:
        base = os.path.splitext(input_file)[0]
        output_file = base + ".musicxml"



    # MIDI 匯入
    score = music21.converter.parse(input_file)


    # 輸出 MusicXML
    score.write(
        "musicxml",
        fp=output_file
    )


    print("MusicXML產生:")
    print(output_file)



    # 清理
    clean_musicxml(output_file)


    return output_file





def clean_musicxml(filename):

    print("開始修正 MusicXML")


    tree = ET.parse(filename)

    root = tree.getroot()



    remove_tags = {

        "backup",
        "forward",
        "grace",
        "octave-change",
        "chord"

    }



    # 找 namespace
    def strip_tag(tag):

        return tag.split("}")[-1]



    # 遞迴刪除
    def clean_element(parent):

        for child in list(parent):

            tag = strip_tag(child.tag)


            if tag in remove_tags:

                parent.remove(child)

            else:

                clean_element(child)



    clean_element(root)



    # 全部 voice 改 1

    for elem in root.iter():

        if strip_tag(elem.tag) == "voice":

            elem.text = "1"



    # 移除空白
    for elem in root.iter():

        if elem.text:

            elem.text = elem.text.strip()



    tree.write(
        filename,
        encoding="utf-8",
        xml_declaration=True
    )



    print("MusicXML修正完成")



if __name__ == "__main__":


    import sys


    if len(sys.argv) < 2:

        print(
            "使用方式:"
            "\npython converter.py input.mid"
        )

        exit()



    midi = sys.argv[1]


    midi_to_musicxml(midi)