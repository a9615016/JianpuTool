import sys
import os
import xml.etree.ElementTree as ET


print("CLEAN VERSION 20260726 V21")


if len(sys.argv) < 2:
    print("usage: python clean_musicxml.py input.musicxml [output.musicxml]")
    sys.exit(1)


input_file = sys.argv[1]

if len(sys.argv) >= 3:
    output_file = sys.argv[2]
else:
    base = os.path.splitext(input_file)[0]
    output_file = base + "_clean.musicxml"


print("input:", input_file)


tree = ET.parse(input_file)
root = tree.getroot()


# namespace
ns = {
    "m": "http://www.musicxml.org/xlink"
}


print("remove voices")


# 移除 voice
for elem in root.iter():
    for child in list(elem):
        if child.tag.endswith("voice"):
            elem.remove(child)


print("remove chords")


# 移除 chord
for elem in root.iter():
    for child in list(elem):
        if child.tag.endswith("chord"):
            elem.remove(child)


print("remove grace")


# 移除 grace
for elem in root.iter():
    for child in list(elem):
        if child.tag.endswith("grace"):
            elem.remove(child)



# ==========================
# V21 強制全部 4/4
# ==========================

print("force time signature V21")


for time in root.iter():

    if time.tag.endswith("time"):

        beats = None
        beat_type = None

        for child in time:
            if child.tag.endswith("beats"):
                beats = child

            if child.tag.endswith("beat-type"):
                beat_type = child


        if beats is None:
            beats = ET.SubElement(time, "beats")

        if beat_type is None:
            beat_type = ET.SubElement(time, "beat-type")


        beats.text = "4"
        beat_type.text = "4"



# ==========================
# V21 修 duration
# ==========================

print("fix durations V21")


for elem in root.iter():

    if elem.tag.endswith("duration"):

        try:

            value = float(elem.text)

            # 避免超大 duration
            if value > 64 or value <= 0:
                print(
                    "fix duration:",
                    value,
                    "-> 4"
                )
                elem.text = "4"


        except:

            elem.text = "4"



# ==========================
# 移除非法 time
# ==========================

print("remove invalid time")


for elem in root.iter():

    if elem.tag.endswith("beats"):

        try:
            if float(elem.text) > 12:
                elem.text = "4"

        except:
            elem.text = "4"


    if elem.tag.endswith("beat-type"):

        try:

            allowed = [
                "1",
                "2",
                "4",
                "8",
                "16"
            ]

            if elem.text not in allowed:
                elem.text = "4"

        except:

            elem.text = "4"



tree.write(
    output_file,
    encoding="utf-8",
    xml_declaration=True
)


print()
print("V21 DONE:")
print(output_file)