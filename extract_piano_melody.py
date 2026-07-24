import xml.etree.ElementTree as ET
import sys


def clean_musicxml(src, dst):

    tree = ET.parse(src)
    root = tree.getroot()


    # namespace
    notes = root.findall(".//note")


    last_pitch = None
    last_duration = None
    remove = []


    for note in notes:

        pitch = note.find("pitch")
        duration = note.find("duration")


        if pitch is None:
            continue


        step = pitch.findtext("step")
        octave = pitch.findtext("octave")


        current = (
            step,
            octave,
            duration.text if duration is not None else ""
        )


        # 移除連續完全相同音符
        if current == last_pitch:

            remove.append(note)

        else:
            last_pitch=current



    for n in remove:

        for parent in root.iter():

            if n in list(parent):

                parent.remove(n)
                break



    # 修正 divisions
    for d in root.findall(".//divisions"):

        d.text="16"



    # 修正時間
    for beats in root.findall(".//beats"):

        beats.text="4"


    for bt in root.findall(".//beat-type"):

        bt.text="4"



    tree.write(
        dst,
        encoding="utf-8",
        xml_declaration=True
    )


    print("clean完成")


if __name__=="__main__":

    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )