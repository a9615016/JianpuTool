import xml.etree.ElementTree as ET
import sys


NS = {
    "m": "http://www.musicxml.org/ns/musicxml"
}

ET.register_namespace("", NS["m"])



def remove_chords(root):

    """
    移除 MusicXML chord 標記
    """

    for parent in root.iter():

        for child in list(parent):

            if child.tag.endswith("chord"):

                parent.remove(child)



def clean_musicxml(input_file, output_file):

    print("開始 clean MusicXML")


    tree = ET.parse(input_file)

    root = tree.getroot()



    # ==========================
    # 移除 credit
    # ==========================

    for parent in root.iter():

        for child in list(parent):

            if child.tag.endswith("credit"):

                parent.remove(child)



    # ==========================
    # 強制 4/4
    # ==========================

    for beats in root.findall(
        ".//m:beats",
        NS
    ):

        beats.text = "4"



    for beat_type in root.findall(
        ".//m:beat-type",
        NS
    ):

        beat_type.text = "4"



    # ==========================
    # octave 修正
    # ==========================

    for octave in root.findall(
        ".//m:octave",
        NS
    ):

        try:

            value = int(octave.text)


            if value < 3:

                octave.text = "3"


            elif value > 6:

                octave.text = "6"


        except:

            octave.text = "4"



    # ==========================
    # duration 修正
    # ==========================

    for duration in root.findall(
        ".//m:duration",
        NS
    ):

        try:

            value = int(duration.text)


            if value <= 0:

                duration.text = "1"


        except:

            duration.text = "1"



    # ==========================
    # voice 統一
    # ==========================

    for voice in root.findall(
        ".//m:voice",
        NS
    ):

        voice.text = "1"



    # ==========================
    # 移除 chord
    # ==========================

    remove_chords(root)



    # ==========================
    # 移除 tie
    # ==========================

    for parent in root.iter():

        for child in list(parent):

            if child.tag.endswith("tie"):

                parent.remove(child)



    # ==========================
    # 輸出
    # ==========================

    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True
    )


    print("clean完成")
    print(output_file)



if __name__ == "__main__":


    if len(sys.argv) < 3:

        print(
            "使用方式:"
            "\npython clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit()



    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )

from music21 import converter, meter


score = converter.parse(input_file)


for part in score.parts:

    part.insert(
        0,
        meter.TimeSignature("4/4")
    )


score.write(
    "musicxml",
    fp=output_file
)