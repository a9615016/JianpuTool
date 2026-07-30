# CLEAN MUSICXML V32
# JianpuTool

VERSION = "V32"

print("CLEAN MUSICXML", VERSION)

import sys
from lxml import etree


INPUT = sys.argv[1]
OUTPUT = sys.argv[2]


tree = etree.parse(INPUT)
root = tree.getroot()


# ==========================
# remove unwanted notation
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

for measure in root.xpath(".//measure"):

    attrs = measure.find("attributes")

    if attrs is None:
        continue

    time = attrs.find("time")

    if time is not None:

        beats = time.find("beats")
        beat_type = time.find("beat-type")

        if beats is not None:
            beats.text = "4"

        if beat_type is not None:
            beat_type.text = "4"



# ==========================
# duration quantize
# ==========================

print("duration quantize")


for duration in root.xpath(".//duration"):

    try:
        value = int(duration.text)

        # quantize to 16 division grid
        value = round(value / 4) * 4

        if value <= 0:
            value = 4

        duration.text = str(value)

    except:
        pass



# ==========================
# rebuild measures check
# ==========================

print("FINAL BAR CHECK V32")


DIVISION = 16
BAR_LENGTH = DIVISION * 4


for measure in root.xpath(".//measure"):

    total = 0

    notes = measure.xpath("./note")


    for note in notes:

        dur = note.find("duration")

        if dur is not None:

            try:
                total += int(dur.text)
            except:
                pass



    if total > BAR_LENGTH:

        print(
            "FIX OVER BAR",
            measure.get("number"),
            total
        )


        overflow = total - BAR_LENGTH


        # 從最後音符開始縮短
        for note in reversed(notes):

            dur = note.find("duration")

            if dur is None:
                continue


            try:
                d = int(dur.text)

            except:
                continue


            if d > overflow:

                dur.text = str(d - overflow)

                break



# ==========================
# remove empty voices
# ==========================

print("clear voices")


for voice in root.xpath(".//voice"):

    parent = voice.getparent()

    if parent is not None:

        parent.remove(voice)



# ==========================
# write
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