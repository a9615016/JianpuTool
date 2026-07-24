import sys
import xml.etree.ElementTree as ET


def clean_musicxml(input_file, output_file):

    print("開始 clean MusicXML")

    tree = ET.parse(input_file)
    root = tree.getroot()


    # 修正所有 note
    for note in root.findall(".//note"):

        pitch = note.find("pitch")

        if pitch is None:
            continue


        step = pitch.find("step")
        octave = pitch.find("octave")


        # 修正 step
        if step is not None:

            if step.text not in [
                "A",
                "B",
                "C",
                "D",
                "E",
                "F",
                "G"
            ]:
                step.text = "C"



        # 修正 octave
        if octave is not None:

            try:
                value = int(octave.text)

            except:
                value = 4


            if value < 1:
                value = 4


            if value > 8:
                value = 4


            octave.text = str(value)



    # 修正 duration
    for d in root.findall(".//duration"):

        try:

            value = int(d.text)

            if value <= 0:
                d.text = "1"

        except:

            d.text = "1"



    # 修正拍號
    for beats in root.findall(".//beats"):

        if beats.text not in [
            "2",
            "3",
            "4",
            "6"
        ]:
            beats.text="4"



    for beat in root.findall(".//beat-type"):

        if beat.text not in [
            "2",
            "4",
            "8"
        ]:
            beat.text="4"



    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True
    )


    print("clean完成")


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