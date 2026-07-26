# clean_musicxml_final.py
# FINAL VERSION
# MusicXML -> jianpu_ly 修正版

import sys
import xml.etree.ElementTree as ET


def clean_musicxml(input_file, output_file):

    print("CLEAN MUSICXML FINAL")

    print("input:")
    print(input_file)

    print("output:")
    print(output_file)


    tree = ET.parse(input_file)
    root = tree.getroot()

    ns = ""

    if root.tag.startswith("{"):
        ns = root.tag.split("}")[0] + "}"


    print("讀取 MusicXML")


    # divisions
    divisions = root.find(
        ".//" + ns + "divisions"
    )

    if divisions is None:
        div_value = 16
    else:
        div_value = int(divisions.text)


    print("divisions:", div_value)



    # =========================
    # 移除 backup / forward
    # =========================

    for elem in root.iter():

        remove = []

        for child in list(elem):

            tag = child.tag.replace(ns, "")

            if tag in [
                "backup",
                "forward"
            ]:
                remove.append(child)


        for r in remove:
            elem.remove(r)



    print("remove backup forward")



    # =========================
    # 移除 chord
    # =========================

    for note in root.iter(ns + "note"):

        chord = note.find(ns + "chord")

        if chord is not None:
            note.remove(chord)



    print("remove chords")



    # =========================
    # 只留第一個 voice
    # =========================

    for measure in root.iter(ns + "measure"):

        voice_found = False

        remove_notes = []


        for note in measure.findall(
            ns + "note"
        ):

            voice = note.find(
                ns + "voice"
            )


            if voice is not None:

                if not voice_found:

                    if voice.text != "1":
                        voice.text = "1"

                    voice_found = True


                else:

                    remove_notes.append(note)



        for n in remove_notes:
            measure.remove(n)



    print("keep voice 1")



    # =========================
    # 修正 duration
    # =========================

    for note in root.iter(ns+"note"):

        duration = note.find(
            ns+"duration"
        )

        if duration is not None:

            value = int(duration.text)


            # 防止過長音符

            if value > div_value*4:

                duration.text = str(
                    div_value*4
                )



    print("fix duration")



    # =========================
    # 移除複雜標記
    # =========================

    remove_tags = [
        "notations",
        "articulations",
        "ornaments",
        "technical",
        "tie",
        "lyric"
    ]


    for tag in remove_tags:

        for elem in root.iter(
            ns+tag
        ):

            parent = None

            for p in root.iter():

                if elem in list(p):

                    parent=p
                    break


            if parent is not None:

                parent.remove(elem)



    print("remove extra tags")



    # =========================
    # 寫入
    # =========================


    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True
    )


    print("完成:")
    print(output_file)



if __name__ == "__main__":


    if len(sys.argv)<3:

        print(
            "python clean_musicxml_final.py input.musicxml output.musicxml"
        )

        sys.exit()


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )