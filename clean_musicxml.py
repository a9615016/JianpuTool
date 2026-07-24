import sys
import xml.etree.ElementTree as ET


def clean_musicxml(input_file, output_file):

    print("開始 clean MusicXML")


    tree = ET.parse(input_file)
    root = tree.getroot()

    ns = "{http://www.musicxml.org/ns/musicxml}"


    # 固定 4/4

    for time in root.findall(".//"+ns+"time"):

        beats=time.find(ns+"beats")
        beat_type=time.find(ns+"beat-type")

        if beats is not None:
            beats.text="4"

        if beat_type is not None:
            beat_type.text="4"



    # =========================
    # 只保留 Voice 1
    # =========================

    for note in root.findall(".//"+ns+"note"):

        voice = note.find(ns+"voice")

        if voice is not None:

            if voice.text != "1":

                # 找父節點刪除

                for measure in root.findall(".//"+ns+"measure"):

                    if note in list(measure):

                        measure.remove(note)
                        break



    # =========================
    # 移除 chord
    # =========================

    for chord in root.findall(".//"+ns+"chord"):

        for note in root.findall(".//"+ns+"note"):

            if chord in list(note):

                note.remove(chord)



    # =========================
    # 移除 grace
    # =========================

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



if __name__=="__main__":

    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )