# bar_check_fix.py
# JianpuTool
# Fix cross measure notes before jianpu_ly

VERSION = "V1"

print("BAR CHECK FIX", VERSION)

import sys
from lxml import etree
from copy import deepcopy


INPUT = sys.argv[1]
OUTPUT = sys.argv[2]


tree = etree.parse(INPUT)
root = tree.getroot()


BAR_LENGTH = 64   # division 16 * 4/4


print("CHECK MEASURES")


measures = root.xpath(".//measure")


for index, measure in enumerate(measures):

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



        # 發現跨小節
        if current + length > BAR_LENGTH:


            overflow = current + length - BAR_LENGTH

            keep = length - overflow


            print(
                "FIX BAR",
                measure.get("number"),
                length,
                "=>",
                keep,
                "+",
                overflow
            )


            # 前半留本小節

            duration.text = str(keep)



            # 後半複製

            new_note = deepcopy(note)


            new_duration = new_note.find("duration")

            if new_duration is not None:

                new_duration.text = str(overflow)



            # 放下一小節

            if index + 1 < len(measures):

                next_measure = measures[index + 1]

                next_measure.insert(
                    0,
                    new_note
                )


            current = BAR_LENGTH


        else:

            current += length



tree.write(
    OUTPUT,
    encoding="utf-8",
    xml_declaration=True
)


print(
    "DONE BAR CHECK FIX",
    VERSION
)