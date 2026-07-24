import xml.etree.ElementTree as ET
import sys


def clean_musicxml(input_file, output_file):

    print("開始 clean MusicXML")

    tree = ET.parse(input_file)
    root = tree.getroot()


    # -----------------------
    # 1. 移除 backup / forward
    # -----------------------

    for parent in root.iter():

        for child in list(parent):

            tag = child.tag.split("}")[-1]

            if tag in ["backup", "forward"]:

                parent.remove(child)



    # -----------------------
    # 2. 移除 pickup / 修正拍號
    # -----------------------

    for measure in root.findall(".//{*}measure"):

        if "implicit" in measure.attrib:

            del measure.attrib["implicit"]


        for time in measure.findall(".//{*}time"):

            beats = time.find("{*}beats")
            beat_type = time.find("{*}beat-type")


            if beats is not None:
                beats.text = "4"


            if beat_type is not None:
                beat_type.text = "4"



    # -----------------------
    # 3. divisions 固定
    # -----------------------

    for div in root.findall(".//{*}divisions"):

        div.text = "16"



    # -----------------------
    # 4. duration 修正
    # -----------------------

    for duration in root.findall(".//{*}duration"):

        try:

            value = int(duration.text)


            if value <= 0:
                duration.text = "1"


            elif value > 16:
                duration.text = "16"


        except:

            duration.text = "1"



    # -----------------------
    # 5. octave 修正
    # -----------------------

    for octave in root.findall(".//{*}octave"):

        try:

            value = int(octave.text)


            if value < 1:
                octave.text = "1"


            elif value > 8:
                octave.text = "8"


        except:

            octave.text = "4"



    # -----------------------
    # 6. 移除重複 chord 音符
    # -----------------------

    last_note = None
    remove_list = []


    for note in root.findall(".//{*}note"):

        pitch = note.find("{*}pitch")

        if pitch is None:
            continue


        step = pitch.findtext("{*}step")
        octave = pitch.findtext("{*}octave")


        current = (
            step,
            octave
        )


        if current == last_note:

            remove_list.append(note)

        else:

            last_note = current



    for note in remove_list:

        for parent in root.iter():

            if note in list(parent):

                parent.remove(note)
                break



    # -----------------------
    # 7. 輸出 UTF-8
    # -----------------------

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
            "使用方式:\n"
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit()


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )