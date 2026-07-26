print("CLEAN VERSION 20260726 V19")

import xml.etree.ElementTree as ET
import sys
import os


def clean(input_file, output_file):

    print("input:", input_file)

    tree = ET.parse(input_file)
    root = tree.getroot()


    # MusicXML namespace
    ns = {
        "m": "http://www.musicxml.org/ns/musicxml"
    }


    # =========================
    # remove voices
    # =========================

    print("remove voices")

    for elem in root.iter():
        for child in list(elem):
            if child.tag.endswith("voice"):
                elem.remove(child)



    # =========================
    # remove chords
    # =========================

    print("remove chords")

    for note in root.iter():
        if note.tag.endswith("note"):

            for child in list(note):
                if child.tag.endswith("chord"):
                    note.remove(child)



    # =========================
    # remove grace
    # =========================

    print("remove grace")

    for note in root.iter():

        if note.tag.endswith("note"):

            for child in list(note):
                if child.tag.endswith("grace"):
                    note.remove(child)



    # =========================
    # FORCE 4/4
    # =========================

    print("force 4/4")


    for measure in root.iter():

        if measure.tag.endswith("measure"):

            has_time = False

            for attr in list(measure):

                if attr.tag.endswith("attributes"):

                    for child in attr:

                        if child.tag.endswith("time"):

                            has_time = True

                            for x in list(child):

                                child.remove(x)


                            beats = ET.Element("beats")
                            beats.text = "4"

                            beat_type = ET.Element("beat-type")
                            beat_type.text = "4"

                            child.append(beats)
                            child.append(beat_type)



            # 沒有拍號補一個
            if not has_time:

                pass



    # =========================
    # FIX INVALID DURATIONS
    # =========================

    print("fix durations")


    valid = {
        1,
        2,
        4,
        8,
        16,
        32
    }


    for duration in root.iter():

        if duration.tag.endswith("duration"):

            try:

                value = int(float(duration.text))

                # 避免 7,14,28 等異常
                if value not in valid:

                    duration.text = "4"


            except:

                duration.text = "4"



    # =========================
    # remove strange time tags
    # =========================

    print("remove invalid time")


    for elem in root.iter():

        if elem.tag.endswith("time-modification"):

            for child in list(elem):

                if child.tag.endswith("actual-notes"):

                    elem.remove(child)



    # =========================
    # WRITE
    # =========================

    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True
    )


    print("V19 DONE:")
    print(output_file)



if __name__ == "__main__":

    if len(sys.argv) < 3:

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit()


    clean(
        sys.argv[1],
        sys.argv[2]
    )
    # ======================================
# CLEAN VERSION 20260726 V19
# Force valid MusicXML for jianpu_ly
# ======================================

print("force time signature 4/4 V19")


# -------------------------
# 修正拍號
# -------------------------

for elem in root.iter():

    if elem.tag.endswith("time"):

        for child in elem:

            if child.tag.endswith("beats"):
                child.text = "4"

            elif child.tag.endswith("beat-type"):
                child.text = "4"



# -------------------------
# divisions 固定 16
# -------------------------

for elem in root.iter():

    if elem.tag.endswith("divisions"):
        elem.text = "16"



# -------------------------
# 移除 jianpu_ly 不支援項目
# -------------------------

remove_tags = [
    "time-modification",
    "tuplet",
    "grace"
]


for parent in root.iter():

    for child in list(parent):

        for tag in remove_tags:

            if child.tag.endswith(tag):
                parent.remove(child)



# -------------------------
# 強制小節完整
# -------------------------

for measure in root.iter():

    if measure.tag.endswith("measure"):

        duration = None

        for child in measure:

            if child.tag.endswith("duration"):
                duration = child
                break


        if duration is not None:

            # 4/4, divisions=16
            # 一小節 = 64
            duration.text = "64"



        print("V19 time fix done")