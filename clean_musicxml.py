import xml.etree.ElementTree as ET
import sys


def clean_musicxml(input_file, output_file):

    print("開始 clean MusicXML")

    tree = ET.parse(input_file)
    root = tree.getroot()


    # 移除 namespace
    for elem in root.iter():
        if "}" in elem.tag:
            elem.tag = elem.tag.split("}",1)[1]


    # =========================
    # 音符清理
    # =========================

    for note in root.iter("note"):

        # 移除 grace
        for g in note.findall("grace"):
            note.remove(g)


        pitch = note.find("pitch")

        if pitch is not None:

            step = pitch.find("step")
            octave = pitch.find("octave")
            alter = pitch.find("alter")


            if step is not None:
                if step.text not in [
                    "A","B","C","D","E","F","G"
                ]:
                    step.text="C"


            if octave is not None:

                try:
                    o=int(octave.text)

                    if o < 1 or o > 8:
                        octave.text="4"

                except:
                    octave.text="4"


            # 移除升降半音
            if alter is not None:

                try:
                    if int(alter.text)!=0:
                        pitch.remove(alter)

                except:
                    pitch.remove(alter)



    # =========================
    # 移除 backup forward
    # =========================

    for measure in root.iter("measure"):

        for b in measure.findall("backup"):
            measure.remove(b)

        for f in measure.findall("forward"):
            measure.remove(f)



    # =========================
    # 修正拍號 4/4
    # =========================

    for time in root.iter("time"):

        beats=time.find("beats")
        beat=time.find("beat-type")

        if beats is not None:
            beats.text="4"

        if beat is not None:
            beat.text="4"



    # =========================
    # 移除 pickup / anacrusis
    # =========================

    for measure in root.iter("measure"):

        if "implicit" in measure.attrib:
            del measure.attrib["implicit"]



    # =========================
    # 第一小節補滿 4/4
    # divisions=16
    # 一小節=64
    # =========================

    first=None

    for m in root.iter("measure"):
        first=m
        break


    if first is not None:

        total=0

        for note in first.findall("note"):

            duration=note.find("duration")

            if duration is not None:

                try:
                    total += int(duration.text)

                except:
                    pass



        if total < 64:

            rest=ET.Element("note")

            ET.SubElement(
                rest,
                "rest"
            )


            duration=ET.SubElement(
                rest,
                "duration"
            )

            duration.text=str(64-total)


            typ=ET.SubElement(
                rest,
                "type"
            )

            typ.text="quarter"


            first.append(rest)



    # =========================
    # 輸出 UTF-8
    # =========================

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