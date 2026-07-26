import sys
import os
import xml.etree.ElementTree as ET
from fractions import Fraction

VERSION = "CLEAN VERSION 20260726 V9"

NS = {
    "m": "http://www.musicxml.org/ns/musicxml"
}

ET.register_namespace("", NS["m"])


def qname(tag):
    return f"{{{NS['m']}}}{tag}"


def get_text(elem, tag, default=None):
    x = elem.find(qname(tag))
    if x is None:
        return default
    return x.text


def set_text(elem, tag, value):
    x = elem.find(qname(tag))
    if x is not None:
        x.text = str(value)


def remove_tag(parent, tag):
    for x in list(parent):
        if x.tag == qname(tag):
            parent.remove(x)


def quantize_duration(duration, divisions):
    """
    四分音符 divisions
    對齊 1/16, 1/8, 1/4
    """

    values = [
        divisions * 4,      # whole
        divisions * 2,      # half
        divisions,          # quarter
        divisions // 2,     # eighth
        divisions // 4      # sixteenth
    ]

    return min(
        values,
        key=lambda x: abs(x - duration)
    )


def clean_musicxml(input_file, output_file):

    print(VERSION)
    print("input:", input_file)

    tree = ET.parse(input_file)
    root = tree.getroot()


    # ==========================
    # divisions
    # ==========================

    divisions = 16

    for div in root.iter(qname("divisions")):
        div.text = str(divisions)


    print("remove voices")

    for note in root.iter(qname("note")):

        remove_tag(note, "voice")
        remove_tag(note, "chord")
        remove_tag(note, "grace")


    print("fix duration")

    # ==========================
    # duration quantize
    # ==========================

    for note in root.iter(qname("note")):

        dur = note.find(qname("duration"))

        if dur is not None:

            try:
                d = int(dur.text)

                new_d = quantize_duration(
                    d,
                    divisions
                )

                dur.text = str(new_d)

            except:
                pass



    print("remove tuplets")

    for tuplet in root.iter(qname("tuplet")):
        parent = None



    print("rebuild measures")


    # ==========================
    # 重建 measure
    # ==========================

    for measure in root.iter(qname("measure")):

        notes = list(
            measure.findall(qname("note"))
        )


        total = 0


        for note in notes:

            dur = note.find(qname("duration"))

            if dur is not None:

                try:
                    total += int(dur.text)
                except:
                    pass



        target = divisions * 4 * 4


        # 超過小節
        if total > target:

            overflow = total - target

            print(
                "trim overflow:",
                overflow
            )


            for note in reversed(notes):

                dur = note.find(
                    qname("duration")
                )

                if dur is None:
                    continue

                d = int(dur.text)


                if overflow >= d:
                    measure.remove(note)
                    overflow -= d

                else:
                    dur.text = str(
                        d - overflow
                    )
                    break



        # 不足補休止符

        elif total < target:

            remain = target - total


            rest = ET.Element(
                qname("note")
            )

            ET.SubElement(
                rest,
                qname("rest")
            )

            duration = ET.SubElement(
                rest,
                qname("duration")
            )

            duration.text = str(remain)


            measure.append(rest)



    print("final cleanup")


    # 移除非法空 duration

    for duration in root.iter(qname("duration")):

        if duration.text is None:
            duration.text = "16"



    print("write")

    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True
    )


    print("done:", output_file)



if __name__ == "__main__":

    if len(sys.argv) < 2:
        print(
            "python clean_musicxml.py input.musicxml [output.musicxml]"
        )
        exit()


    inp = sys.argv[1]

    if len(sys.argv) >= 3:
        out = sys.argv[2]
    else:
        out = os.path.splitext(inp)[0] + "_clean.musicxml"


    clean_musicxml(
        inp,
        out
    )