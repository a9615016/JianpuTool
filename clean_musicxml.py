import xml.etree.ElementTree as ET
import sys


def clean_musicxml(input_file, output_file):

    print("開始 clean MusicXML")

    tree = ET.parse(input_file)
    root = tree.getroot()


    # remove namespace
    for elem in root.iter():
        if "}" in elem.tag:
            elem.tag = elem.tag.split("}", 1)[1]


    # =========================
    # divisions 強制 16
    # =========================

    for div in root.iter("divisions"):
        div.text = "16"



    # =========================
    # note 清理
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



            # 移除升降記號
            if alter is not None:

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
    # 移除 pickup / anacrusis
    # =========================

    for measure in root.iter("measure"):


        if "implicit" in measure.attrib:
            del measure.attrib["implicit"]



        if measure.attrib.get("number")=="0":

            measure.attrib["number"]="1"



        attrs=measure.find("attributes")


        if attrs is not None:

            for ms in attrs.findall("measure-style"):

                attrs.remove(ms)




    # =========================
    # 強制 4/4
    # =========================

    for time in root.iter("time"):

        beats=time.find("beats")
        beat_type=time.find("beat-type")


        if beats is not None:
            beats.text="4"


        if beat_type is not None:
            beat_type.text="4"




    # =========================
    # 第一小節補滿
    # =========================

    first_measure=None


    for m in root.iter("measure"):

        first_measure=m
        break



    if first_measure is not None:


        total=0


        for note in first_measure.findall("note"):


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



            first_measure.append(rest)




    # =========================
    # 輸出
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

        exit()



    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )