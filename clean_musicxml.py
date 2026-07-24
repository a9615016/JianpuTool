import sys
import xml.etree.ElementTree as ET


def clean_musicxml(input_file, output_file):

    print("開始 clean MusicXML")


    tree = ET.parse(input_file)
    root = tree.getroot()

    ns = "{http://www.musicxml.org/ns/musicxml}"


    # -------------------------
    # 1. 固定 4/4
    # -------------------------

    for time in root.findall(".//"+ns+"time"):

        beats=time.find(ns+"beats")
        beat_type=time.find(ns+"beat-type")

        if beats is not None:
            beats.text="4"

        if beat_type is not None:
            beat_type.text="4"



    # -------------------------
    # 2. 移除 chord
    # 保留第一個音
    # -------------------------

    for measure in root.findall(".//"+ns+"measure"):

        notes = measure.findall(ns+"note")

        chord_found=False

        for note in notes:

            chord = note.find(ns+"chord")

            if chord is not None:

                # 刪掉後續和弦音
                if chord_found:
                    measure.remove(note)

                else:
                    note.remove(chord)
                    chord_found=True

            else:
                chord_found=False



    # -------------------------
    # 3. 移除 grace note
    # -------------------------

    for grace in root.findall(".//"+ns+"grace"):

        parent=None

        for p in root.iter():

            if grace in list(p):
                parent=p
                break


        if parent is not None:

            note=parent

            if note.tag==ns+"note":

                for x in note.findall(ns+"grace"):
                    note.remove(x)



    # -------------------------
    # 4. 移除八度記號問題來源
    # -------------------------

    for note in root.findall(".//"+ns+"note"):

        pitch=note.find(ns+"pitch")

        if pitch is not None:

            octave=pitch.find(ns+"octave")

            if octave is not None:

                try:
                    value=int(octave.text)

                    # 限制正常音域
                    if value < 1:
                        octave.text="1"

                    if value > 7:
                        octave.text="7"

                except:
                    octave.text="4"



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