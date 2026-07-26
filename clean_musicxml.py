import sys
import xml.etree.ElementTree as ET
from copy import deepcopy


print("CLEAN MUSICXML FINAL V2")


if len(sys.argv) < 3:
    print("usage: python clean_musicxml_final.py input.musicxml output.musicxml")
    sys.exit(1)


input_file = sys.argv[1]
output_file = sys.argv[2]


print("input:")
print(input_file)

print("output:")
print(output_file)


NS = {
    "": "http://www.musicxml.org/ns/musicxml"
}


ET.register_namespace("", "http://www.musicxml.org/ns/musicxml")


tree = ET.parse(input_file)
root = tree.getroot()


print("讀取 MusicXML")


# -------------------------------------------------
# 1. divisions 固定
# -------------------------------------------------

for div in root.iter("divisions"):
    div.text = "16"

print("set divisions = 16")


# -------------------------------------------------
# 2. 移除 chord
# -------------------------------------------------

for note in root.iter("note"):
    for child in list(note):
        if child.tag == "chord":
            note.remove(child)

print("remove chord")


# -------------------------------------------------
# 3. 只留 voice 1
# -------------------------------------------------

for measure in root.iter("measure"):

    for note in list(measure):

        if note.tag.endswith("note"):

            voice = note.find("voice")

            if voice is not None:
                if voice.text != "1":
                    measure.remove(note)


print("keep voice 1")


# -------------------------------------------------
# 4. duration 量化
# -------------------------------------------------

for duration in root.iter("duration"):

    try:
        value = int(duration.text)

        # 10080 PPQ轉16格
        new_value = round(value / 630)

        if new_value < 1:
            new_value = 1

        duration.text = str(new_value)

    except:
        pass


print("quantize duration")


# -------------------------------------------------
# 5. 修正小節長度
# -------------------------------------------------

BAR_LENGTH = 64


for measure in root.iter("measure"):

    total = 0

    notes = []

    for note in list(measure):

        if note.tag.endswith("note"):

            dur = note.find("duration")

            if dur is not None:

                try:
                    d = int(dur.text)

                    total += d

                    notes.append(note)

                except:
                    pass


    # 超過小節
    while total > BAR_LENGTH:

        excess = total - BAR_LENGTH


        if notes:

            last = notes[-1]

            dur = last.find("duration")


            if dur is not None:

                old = int(dur.text)

                new = old - excess


                if new > 0:

                    dur.text = str(new)

                    print(
                        "trim note",
                        excess
                    )

                else:

                    dur.text = "1"


        break



    # 不足補 rest

    if total < BAR_LENGTH:

        rest = ET.Element("note")


        ET.SubElement(rest,"rest")


        ET.SubElement(
            rest,
            "duration"
        ).text = str(
            BAR_LENGTH-total
        )


        ET.SubElement(
            rest,
            "voice"
        ).text="1"


        measure.append(rest)



print("fix measure length")


# -------------------------------------------------
# 6. 移除多餘 tag
# -------------------------------------------------

remove_tags = [
    "backup",
    "forward",
    "print",
    "sound"
]


for tag in remove_tags:

    for elem in root.iter(tag):

        parent = None

        for p in root.iter():

            if elem in list(p):
                parent=p
                break


        if parent is not None:

            parent.remove(elem)



print("remove extra tags")


tree.write(
    output_file,
    encoding="utf-8",
    xml_declaration=True
)


print("完成:")
print(output_file)