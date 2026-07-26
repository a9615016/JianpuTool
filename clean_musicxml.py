import sys
import xml.etree.ElementTree as ET


print("CLEAN VERSION 20260726 V20")


def clean(input_file, output_file):

    print("input:", input_file)

    tree = ET.parse(input_file)
    root = tree.getroot()


    # namespace
    ns = ""

    if root.tag.startswith("{"):
        ns = root.tag.split("}")[0] + "}"


    print("remove voices")
    for elem in root.iter(ns + "voice"):
        elem.text = "1"


    print("remove chords")
    for elem in root.iter(ns + "chord"):
        parent = None


    print("remove grace")
    for elem in root.iter(ns + "grace"):
        elem.clear()


    print("force 4/4")

    for measure in root.iter(ns + "measure"):

        attributes = measure.find(ns + "attributes")

        if attributes is not None:

            time = attributes.find(ns + "time")

            if time is not None:

                beats = time.find(ns + "beats")
                beat_type = time.find(ns + "beat-type")

                if beats is not None:
                    beats.text = "4"

                if beat_type is not None:
                    beat_type.text = "4"



    print("fix durations V20")

    # 修正 jianpu_ly 不接受的 duration

    valid = [
        0.5,
        0.75,
        1,
        1.5,
        2,
        3,
        4,
        6,
        8,
        12
    ]


    for duration in root.iter(ns + "duration"):

        try:

            value = float(duration.text)


            # jianpu_ly 禁止奇怪長度
            if value not in valid:

                print(
                    "fix duration:",
                    value,
                    "-> 4"
                )

                duration.text = "4"


        except:

            pass



    print("remove invalid time")

    for time_mod in root.iter(ns + "time-modification"):

        parent = None



    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True
    )


    print("V20 DONE:")
    print(output_file)



if __name__ == "__main__":

    if len(sys.argv) < 3:
        print(
            "usage: python clean_musicxml.py input.musicxml output.musicxml"
        )
        sys.exit(1)


    clean(
        sys.argv[1],
        sys.argv[2]
    )