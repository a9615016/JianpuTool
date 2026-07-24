import sys
import xml.etree.ElementTree as ET


def clean_musicxml(input_file, output_file):

    print("開始 clean MusicXML")

    tree = ET.parse(input_file)
    root = tree.getroot()

    ns = "{http://www.musicxml.org/ns/musicxml}"


    # 固定 4/4

    for time in root.findall(".//"+ns+"time"):

        beats = time.find(ns+"beats")
        beat_type = time.find(ns+"beat-type")

        if beats is not None:
            beats.text = "4"

        if beat_type is not None:
            beat_type.text = "4"



    # ======================
    # 移除所有 chord note
    # ======================

    for measure in root.findall(".//"+ns+"measure"):

        notes = list(measure.findall(ns+"note"))

        first_note = True

        for note in notes:

            chord = note.find(ns+"chord")

            if chord is not None:
                measure.remove(note)
                continue



    # ======================
    # 移除同時間重複音
    # 保留第一個
    # ======================

    for measure in root.findall(".//"+ns+"measure"):

        seen = set()

        for note in list(measure.findall(ns+"note")):

            pitch = note.find(ns+"pitch")

            if pitch is None:
                continue


            step = pitch.find(ns+"step")
            octave = pitch.find(ns+"octave")


            if step is not None and octave is not None:

                key = (
                    step.text,
                    octave.text
                )


                if key in seen:
                    measure.remove(note)

                else:
                    seen.add(key)



    # ======================
    # 移除 grace
    # ======================

    for grace in root.findall(".//"+ns+"grace"):

        for note in root.findall(".//"+ns+"note"):

            if grace in list(note):
                note.remove(grace)



    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True
    )


    print("clean完成")
    print(output_file)



if __name__ == "__main__":

    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )