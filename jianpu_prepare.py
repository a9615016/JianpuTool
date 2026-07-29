#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
jianpu_prepare.py

MusicXML -> jianpu_ly 前處理
修正：
- backup / forward
- voice 多層
- chord
- 小節長度
"""

import sys
from pathlib import Path
from lxml import etree


DIVISION_DEFAULT = 16
BEAT = 4


def qlen(duration, divisions):
    return duration / divisions


def make_rest(duration):
    rest = etree.Element("note")

    etree.SubElement(rest, "rest")

    dur = etree.SubElement(rest, "duration")
    dur.text = str(duration)

    voice = etree.SubElement(rest, "voice")
    voice.text = "1"

    return rest


def prepare(input_file, output_file):

    print("LOAD:", input_file)

    tree = etree.parse(input_file)
    root = tree.getroot()

    divisions = DIVISION_DEFAULT

    div = root.find(".//divisions")
    if div is not None:
        divisions = int(div.text)

    print("DIVISIONS:", divisions)


    # -------------------------
    # 清理 note
    # -------------------------

    for measure in root.xpath(".//measure"):

        current = 0
        notes = []

        for item in list(measure):

            tag = etree.QName(item).localname


            # remove backup
            if tag == "backup":
                measure.remove(item)
                print("remove backup")
                continue


            # remove forward
            if tag == "forward":
                measure.remove(item)
                print("remove forward")
                continue


            if tag != "note":
                continue


            # remove chord
            chord = item.find("chord")
            if chord is not None:
                item.remove(chord)


            # force voice 1
            voice = item.find("voice")
            if voice is None:
                voice = etree.SubElement(item, "voice")

            voice.text = "1"


            duration = item.find("duration")

            if duration is None:
                continue


            d = int(duration.text)

            current += d

            notes.append(item)


        # -------------------------
        # 補滿小節
        # -------------------------

        measure_target = divisions * BEAT


        if current < measure_target:

            missing = measure_target-current

            print(
                "Measure",
                measure.get("number"),
                "fill rest",
                missing
            )

            rest = make_rest(missing)

            measure.append(rest)

            current += missing


        print(
            "Measure",
            measure.get("number"),
            qlen(current, divisions)
        )


    # -------------------------
    # 移除 notation cache
    # -------------------------

    for x in root.xpath(".//notations"):
        parent = x.getparent()

        if parent is not None:
            parent.remove(x)

    print("clear notation cache")


    tree.write(
        output_file,
        encoding="UTF-8",
        xml_declaration=True
    )


    print()
    print("DONE")
    print(output_file)



if __name__ == "__main__":

    if len(sys.argv) < 3:
        print(
            "Usage:"
        )
        print(
            "python jianpu_prepare.py input.musicxml output.musicxml"
        )
        sys.exit(1)


    prepare(
        sys.argv[1],
        sys.argv[2]
    )