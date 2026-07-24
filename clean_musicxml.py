import xml.etree.ElementTree as ET
import sys
import os


def clean_musicxml(input_file, output_file):

    print("開始 clean MusicXML")

    tree = ET.parse(input_file)
    root = tree.getroot()

    ns = ""

    # 移除 namespace
    for elem in root.iter():
        if "}" in elem.tag:
            elem.tag = elem.tag.split("}",1)[1]


    # 修正所有 note
    for note in root.iter("note"):

        # 移除不支援 grace
        for grace in note.findall("grace"):
            note.remove(grace)


        pitch = note.find("pitch")

        if pitch is not None:

            step = pitch.find("step")
            octave = pitch.find("octave")
            alter = pitch.find("alter")


            # 修正空 step
            if step is not None:
                if step.text not in [
                    "A","B","C","D","E","F","G"
                ]:
                    step.text = "C"


            # 修正 octave
            if octave is not None:

                try:
                    value=int(octave.text)

                    # jianpu_ly 建議範圍
                    if value < 0:
                        octave.text="4"

                    if value > 9:
                        octave.text="4"


                except:
                    octave.text="4"


            # 移除 alter 避免半音錯誤
            if alter is not None:
                try:
                    a=int(alter.text)
                    if a != 0:
                        note.remove(alter)
                except:
                    note.remove(alter)


    # 移除 backup 避免 -2 -6 position 錯誤
    for measure in root.iter("measure"):

        for backup in measure.findall("backup"):
            measure.remove(backup)


        for forward in measure.findall("forward"):
            measure.remove(forward)



    # 修正 time signature

    for time in root.iter("time"):

        beats=time.find("beats")
        beat_type=time.find("beat-type")

        if beats is not None:
            beats.text="4"

        if beat_type is not None:
            beat_type.text="4"



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
        sys.exit()


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )