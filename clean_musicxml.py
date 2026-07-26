import sys
import xml.etree.ElementTree as ET
import os


print("CLEAN VERSION 20260726 V21")

if len(sys.argv) < 2:
    print("usage: python clean_musicxml.py input.musicxml output.musicxml")
    sys.exit(1)

input_file = sys.argv[1]

if len(sys.argv) >= 3:
    output_file = sys.argv[2]
else:
    output_file = input_file.replace(
        ".musicxml",
        "_clean.musicxml"
    )


print("input:", input_file)


tree = ET.parse(input_file)
root = tree.getroot()


ns = {
    "m": "http://www.musicxml.org/ns/musicxml"
}


def tag(x):
    return x.tag.split("}")[-1]


print("remove voices")
for elem in root.iter():
    if tag(elem) == "voice":
        elem.text = "1"


print("remove chords")
for note in root.iter():
    if tag(note) == "note":
        for child in list(note):
            if tag(child) == "chord":
                note.remove(child)


print("remove grace")
for note in root.iter():
    if tag(note) == "note":
        for child in list(note):
            if tag(child) == "grace":
                note.remove(child)


print("force 4/4")


# 修正所有拍號
for measure in root.iter():
    if tag(measure) == "attributes":

        for time in measure:
            if tag(time) == "time":

                beats = None
                beat_type = None

                for x in time:
                    if tag(x) == "beats":
                        beats = x
                    if tag(x) == "beat-type":
                        beat_type = x

                if beats is not None:
                    beats.text = "4"

                if beat_type is not None:
                    beat_type.text = "4"


print("fix measure duration V21")


# 移除可能造成 jianpu_ly KeyError 的異常資訊
for elem in root.iter():

    if tag(elem) == "measure-style":

        parent = None

        for child in list(elem):
            if tag(child) in [
                "multiple-rest",
                "measure-repeat"
            ]:
                elem.remove(child)


# 修正 divisions
for elem in root.iter():

    if tag(elem) == "divisions":

        try:
            value = int(elem.text)

            if value <= 0:
                elem.text = "1"

        except:
            elem.text = "1"



print("remove invalid time")


# 最後保證不存在奇怪 time signature
for elem in root.iter():

    if tag(elem) == "time":

        beats = None
        beat = None

        for c in elem:
            if tag(c) == "beats":
                beats = c
            if tag(c) == "beat-type":
                beat = c


        if beats is None:
            beats = ET.SubElement(elem, "beats")

        if beat is None:
            beat = ET.SubElement(elem, "beat-type")


        beats.text = "4"
        beat.text = "4"



tree.write(
    output_file,
    encoding="utf-8",
    xml_declaration=True
)


print("V21 DONE:")
print(output_file)