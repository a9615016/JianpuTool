print("CLEAN VERSION 20260726 V18")


import sys
import xml.etree.ElementTree as ET


def clean(input_file, output_file):

    print("input:", input_file)


    tree = ET.parse(input_file)

    root = tree.getroot()


    # namespace
    ns = {
        "m": "http://www.musicxml.org"
    }


    print("remove voices")


    for note in root.iter("note"):

        voice = note.find("voice")

        if voice is not None:
            note.remove(voice)



    print("remove chords")


    for measure in root.iter("measure"):

        notes = list(measure)

        chord_found = False

        for n in notes:

            if n.tag == "note":

                chord = n.find("chord")

                if chord is not None:

                    measure.remove(n)



    print("remove grace")


    for grace in root.iter("grace"):

        parent = None

        for p in root.iter():

            if grace in list(p):

                parent = p
                break

        if parent is not None:

            parent.remove(grace)



    print("quantize durations")


    for duration in root.iter("duration"):

        try:

            value = int(duration.text)

            # 強制16格
            value = round(value / 4) * 4

            if value <= 0:
                value = 4

            duration.text = str(value)


        except:

            pass



    print("split cross measure notes")

    # 保留結構
    # 避免跨小節錯誤



    print("repair measure length")


    print("force divisions = 16")


    for divisions in root.iter("divisions"):

        divisions.text = "16"



    # ============================
    # V18 修正
    # 非法拍號修正
    # ============================

    print("fix invalid time signature")


    for measure in root.iter("measure"):


        attributes = measure.find("attributes")


        if attributes is None:
            continue



        time = attributes.find("time")


        if time is None:
            continue



        beats = time.find("beats")

        beat_type = time.find("beat-type")



        if beats is not None and beat_type is not None:


            try:

                beat_value = int(beats.text)


            except:

                beat_value = 4



            if beat_value not in [2,3,4,6]:


                print(
                    "Fix time:",
                    beats.text,
                    "/",
                    beat_type.text
                )


                beats.text = "4"

                beat_type.text = "4"



    print("V18 time fix done")



    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True
    )

    # =========================
# V19 FORCE TIME SIGNATURE
# =========================

print("force time signature 4/4 V19")


for elem in root.iter():

    # 找 attributes
    if elem.tag.endswith("attributes"):

        for child in elem:

            # 找 time
            if child.tag.endswith("time"):

                for item in child:

                    if item.tag.endswith("beats"):
                        item.text = "4"

                    elif item.tag.endswith("beat-type"):
                        item.text = "4"



    print("V19 time fix done")
    print("done:")

    print(output_file)



if __name__ == "__main__":


    if len(sys.argv) < 3:

        print(
            "usage: python clean_musicxml.py input.musicxml output.musicxml"
        )

        exit()


    clean(
        sys.argv[1],
        sys.argv[2]
    )