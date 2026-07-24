import xml.etree.ElementTree as ET
import sys


def clean_musicxml(input_file, output_file):

    print("開始 clean MusicXML")

    tree = ET.parse(input_file)
    root = tree.getroot()


    # -------------------------
    # 1. 移除重複 chord 音符
    # -------------------------

    last_note = None
    remove_list = []

    for note in root.findall(".//note"):

        pitch = note.find("pitch")
        duration = note.find("duration")

        if pitch is None:
            continue

        step = pitch.findtext("step")
        alter = pitch.findtext("alter", "0")
        octave = pitch.findtext("octave")

        dur = ""

        if duration is not None:
            dur = duration.text


        current = (
            step,
            alter,
            octave,
            dur
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



    # -------------------------
    # 2. 修正 octave
    # -------------------------

    for octave in root.findall(".//octave"):

        try:

            value = int(octave.text)

            if value < 1:
                octave.text = "1"

            if value > 8:
                octave.text = "8"


        except:

            octave.text = "4"



    # -------------------------
    # 3. 修正 divisions
    # -------------------------

    for div in root.findall(".//divisions"):

        div.text = "16"



    # -------------------------
    # 4. 修正拍號
    # 避免 KeyError 24
    # -------------------------

    for beats in root.findall(".//beats"):

        beats.text = "4"


    for beat_type in root.findall(".//beat-type"):

        beat_type.text = "4"



    # -------------------------
    # 5. 修正 duration
    # -------------------------

    for duration in root.findall(".//duration"):

        try:

            value = int(duration.text)


            # jianpu_ly 支援範圍
            if value <= 0:
                duration.text = "1"


            elif value > 16:
                duration.text = "16"


        except:

            duration.text = "1"



    # -------------------------
    # 6. 移除 pickup / measure-style
    # -------------------------

    for measure in root.findall(".//measure"):

        for attr in measure.findall("./attributes"):

            for ts in attr.findall("./time"):

                measure.remove(attr)


    # -------------------------
    # 7. UTF-8 輸出
    # -------------------------

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