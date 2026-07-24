import xml.etree.ElementTree as ET
import sys
import os


def clean_musicxml(input_file, output_file):

    print("開始 clean MusicXML")

    tree = ET.parse(input_file)
    root = tree.getroot()


    # 移除 namespace
    for elem in root.iter():
        if "}" in elem.tag:
            elem.tag = elem.tag.split("}", 1)[1]


    # =========================
    # 修正音符
    # =========================

    for note in root.iter("note"):

        # 移除 grace
        for grace in note.findall("grace"):
            note.remove(grace)


        pitch = note.find("pitch")

        if pitch is not None:

            step = pitch.find("step")
            octave = pitch.find("octave")
            alter = pitch.find("alter")


            # step 修正
            if step is not None:

                if step.text not in [
                    "A","B","C","D","E","F","G"
                ]:
                    step.text="C"


            # octave 修正
            if octave is not None:

                try:
                    value=int(octave.text)

                    if value < 1 or value > 8:
                        octave.text="4"

                except:
                    octave.text="4"



            # 移除升降記號
            if alter is not None:

                try:

                    if int(alter.text)!=0:
                        pitch.remove(alter)

                except:

                    pitch.remove(alter)



    # =========================
    # 移除 backup / forward
    # 避免 jianpu_ly position 錯誤
    # =========================

    for measure in root.iter("measure"):

        for backup in measure.findall("backup"):
            measure.remove(backup)


        for forward in measure.findall("forward"):
            measure.remove(forward)



    # =========================
    # 移除 pickup / anacrusis
    # =========================

    for measure in root.iter("measure"):

        attrs = measure.find("attributes")

        if attrs is not None:

            for ms in attrs.findall("measure-style"):
                attrs.remove(ms)



    # =========================
    # 修正拍號 4/4
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
                    total+=int(duration.text)

                except:
                    pass



        # divisions=16
        # 4/4 = 64

        if total < 64:

            diff=64-total


            notes=first_measure.findall("note")


            if notes:

                duration=notes[-1].find("duration")

                if duration is not None:

                    try:
                        old=int(duration.text)
                        duration.text=str(old+diff)

                    except:
                        pass



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

        sys.exit()



    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )