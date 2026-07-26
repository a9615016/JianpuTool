import sys
import xml.etree.ElementTree as ET


print("CLEAN VERSION 20260726 V19")


if len(sys.argv) < 3:
    print("usage: python clean_musicxml.py input.musicxml output.musicxml")
    sys.exit(1)


input_file = sys.argv[1]
output_file = sys.argv[2]


print("input:", input_file)


tree = ET.parse(input_file)

root = tree.getroot()


ns = {
    "m": "http://www.musicxml.org/ns/musicxml"
}


# =========================
# remove voices
# =========================

print("remove voices")

for elem in root.iter():
    tag = elem.tag.split("}")[-1]

    if tag == "voice":
        elem.clear()



# =========================
# remove chords
# =========================

print("remove chords")

for elem in root.iter():
    tag = elem.tag.split("}")[-1]

    if tag == "chord":
        parent = None



# =========================
# remove grace notes
# =========================

print("remove grace")

for elem in root.iter():
    tag = elem.tag.split("}")[-1]

    if tag == "grace":
        elem.clear()



# =========================
# force 4/4
# =========================

print("force 4/4")


for elem in root.iter():

    tag = elem.tag.split("}")[-1]

    if tag == "time":

        for child in list(elem):

            ctag = child.tag.split("}")[-1]

            if ctag == "beats":
                child.text = "4"

            elif ctag == "beat-type":
                child.text = "4"



# =========================
# fix invalid duration
# =========================

print("fix durations")


for elem in root.iter():

    tag = elem.tag.split("}")[-1]

    if tag == "duration":

        try:
            value = int(elem.text)

            if value <= 0:
                elem.text = "1"

        except:
            elem.text = "1"



# =========================
# remove invalid time
# =========================

print("remove invalid time")


# divisions 固定

for elem in root.iter():

    tag = elem.tag.split("}")[-1]

    if tag == "divisions":

        elem.text = "16"



print("V19 DONE:")


tree.write(
    output_file,
    encoding="utf-8",
    xml_declaration=True
)


print(output_file)