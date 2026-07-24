import sys
import xml.etree.ElementTree as ET


def clean_musicxml(input_file, output_file):

    print("開始 clean MusicXML")

    tree = ET.parse(input_file)
    root = tree.getroot()


    # 修正 note pitch

    for note in root.findall(".//note"):

        pitch = note.find("pitch")

        if pitch is None:
            continue


        step = pitch.find("step")
        octave = pitch.find("octave")


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



        if octave is not None:

            try:
                value=int(octave.text)

            except:
                value=4


            if value < 2:
                value=4

            if value > 7:
                value=4


            octave.text=str(value)



        # 移除異常 pitch alter

        alter = pitch.find("alter")

        if alter is not None:

            try:
                a=float(alter.text)

                if a not in [-2,-1,0,1,2]:
                    pitch.remove(alter)

            except:

                pitch.remove(alter)



    # 修正 voice

    for voice in root.findall(".//voice"):

        if voice.text is None:

            voice.text="1"



    # 修正 duration

    for d in root.findall(".//duration"):

        try:

            if int(d.text)<=0:

                d.text="1"

        except:

            d.text="1"



    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True
    )


    print("clean完成")



if __name__=="__main__":


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )