# CLEAN MUSICXML V33
# JianpuTool

VERSION = "V33"

print("CLEAN MUSICXML", VERSION)

import sys
from lxml import etree
from copy import deepcopy


INPUT = sys.argv[1]
OUTPUT = sys.argv[2]


tree = etree.parse(INPUT)
root = tree.getroot()


DIVISION = 16
BAR_LENGTH = 64


# ==========================
# remove notation
# ==========================

print("remove chords")

for chord in root.xpath(".//chord"):
    parent = chord.getparent()
    if parent is not None:
        parent.remove(chord)


print("remove beams")

for beam in root.xpath(".//beam"):
    parent = beam.getparent()
    if parent is not None:
        parent.remove(beam)


print("remove ties")

for tie in root.xpath(".//tie"):
    parent = tie.getparent()
    if parent is not None:
        parent.remove(tie)



# ==========================
# force 4/4
# ==========================

print("force 4/4")

for time in root.xpath(".//time"):

    beats = time.find("beats")
    beat_type = time.find("beat-type")

    if beats is not None:
        beats.text = "4"

    if beat_type is not None:
        beat_type.text = "4"



# ==========================
# quantize
# ==========================

print("duration quantize")

for d in root.xpath(".//duration"):

    try:
        value = int(d.text)
        value = max(4, round(value / 4) * 4)
        d.text = str(value)

    except:
        pass



# ==========================
# SPLIT CROSS MEASURE NOTES
# ==========================

print("SPLIT CROSS MEASURE NOTES V33")


for measure in root.xpath(".//measure"):

    current = 0

    notes = measure.xpath("./note")


    for note in notes[:]:

        duration = note.find("duration")

        if duration is None:
            continue


        try:
            length = int(duration.text)

        except:
            continue



        # 超過小節線
        if current + length > BAR_LENGTH:

            overflow = current + length - BAR_LENGTH

            first = length - overflow


            print(
                "SPLIT NOTE",
                measure.get("number"),
                length,
                "->",
                first,
                "+",
                overflow
            )


            # 原 note 留前半
            duration.text = str(first)



            # 建立下一段
            second = deepcopy(note)

            second_duration = second.find("duration")

            if second_duration is not None:
                second_duration.text = str(overflow)



            # 加入下一個小節
            next_measure = measure.getnext()


            if next_measure is not None:

                next_measure.insert(
                    0,
                    second
                )


            current = BAR_LENGTH


        else:

            current += length



# ==========================
# remove voices
# ==========================

print("remove voices")

for voice in root.xpath(".//voice"):

    parent = voice.getparent()

    if parent is not None:
        parent.remove(voice)



# ==========================
# save
# ==========================

tree.write(
    OUTPUT,
    encoding="utf-8",
    xml_declaration=True
)


print(
    "DONE CLEAN MUSICXML",
    VERSION
)