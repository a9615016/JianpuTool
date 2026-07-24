import xml.etree.ElementTree as ET
import sys


NS = {
    "m": "http://www.musicxml.org/ns/musicxml"
}

ET.register_namespace("", NS["m"])


def clean_musicxml(input_file, output_file):

    print("開始 clean MusicXML")


    tree = ET.parse(input_file)

    root = tree.getroot()



    # ==========================
    # 移除 credit
    # ==========================

    for credit in root.findall(".//m:credit", NS):

        parent = root

        try:
            parent.remove(credit)
        except:
            pass



    # ==========================
    # 強制 4/4
    # ==========================

    for beats in root.findall(".//m:beats", NS):

        beats.text = "4"


    for beat_type in root.findall(".//m:beat-type", NS):

        beat_type.text = "4"



    # ==========================
    # 只保留 voice 1
    # ==========================

    for voice in root.findall(".//m:voice", NS):

        if voice.text != "1":

            parent = None



    # ==========================
    # 移除 chord 標記
    # ==========================

    for chord in root.findall(".//m:chord", NS):

        parent = None

        # 找不到 parent 用重建方式處理
        chord.clear()



    # ==========================
    # 修正 octave
    # ==========================

    for step in root.findall(".//m:step", NS):

        if step.text is None:
            continue


    for octave in root.findall(".//m:octave", NS):

        try:

            value = int(octave.text)


            if value < 3:
                octave.text = "3"


            if value > 6:
                octave.text = "6"


        except:

            octave.text="4"



    # ==========================
    # 修正 duration
    # ==========================

    for duration in root.findall(".//m:duration", NS):

        try:

            d=int(duration.text)

            if d <=0:
                duration.text="1"


        except:

            duration.text="1"



    # ==========================
    # 移除 tie
    # ==========================

    for tie in root.findall(".//m:tie", NS):

        parent=None



    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True
    )


    print("clean完成")
    print(output_file)



if __name__=="__main__":


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )