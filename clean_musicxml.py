# clean_musicxml.py V12
# 強制每小節=64量化版

import sys
import xml.etree.ElementTree as ET
import copy

NS = {"m": "http://www.musicxml.org/ns/musicxml"}

ET.register_namespace("", "http://www.musicxml.org/ns/musicxml")


TARGET_DURATION = 64


def get_duration(note):
    d = note.find("m:duration", NS)
    if d is not None:
        return int(d.text)
    return 0


def set_duration(note, value):
    d = note.find("m:duration", NS)
    if d is not None:
        d.text = str(value)


def create_rest(duration):

    note = ET.Element(
        "{http://www.musicxml.org/ns/musicxml}note"
    )

    rest = ET.SubElement(
        note,
        "{http://www.musicxml.org/ns/musicxml}rest"
    )

    duration_node = ET.SubElement(
        note,
        "{http://www.musicxml.org/ns/musicxml}duration"
    )

    duration_node.text = str(duration)

    type_node = ET.SubElement(
        note,
        "{http://www.musicxml.org/ns/musicxml}type"
    )

    type_node.text = "quarter"

    return note



def fix_measure(measure):

    notes = []

    for child in list(measure):

        if child.tag.endswith("note"):
            notes.append(child)


    total = sum(get_duration(n) for n in notes)


    print(
        "measure",
        measure.find("m:measure-number",NS),
        "duration=",
        total
    )


    # 太長，裁切
    if total > TARGET_DURATION:

        current = 0

        for note in notes:

            dur = get_duration(note)

            if current + dur <= TARGET_DURATION:

                current += dur

            else:

                remain = TARGET_DURATION-current

                if remain > 0:
                    set_duration(note, remain)
                    current = TARGET_DURATION

                else:
                    measure.remove(note)

        return


    # 太短，補休止
    if total < TARGET_DURATION:

        remain = TARGET_DURATION-total

        rest = create_rest(remain)

        measure.append(rest)




def clean(input_file, output_file):

    print("CLEAN VERSION 20260726 V12")

    print("input:",input_file)


    tree = ET.parse(input_file)

    root = tree.getroot()


    # 移除 voices/chords/grace
    for elem in root.iter():

        for child in list(elem):

            tag = child.tag.split("}")[-1]

            if tag in [
                "voice",
                "chord",
                "grace",
                "tuplet"
            ]:
                elem.remove(child)



    # divisions固定16
    for div in root.iter(
        "{http://www.musicxml.org/ns/musicxml}divisions"
    ):
        div.text="16"



    # 修小節
    for measure in root.iter(
        "{http://www.musicxml.org/ns/musicxml}measure"
    ):

        fix_measure(measure)



    print("final cleanup")

    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True
    )


    print("done:",output_file)



if __name__=="__main__":

    if len(sys.argv)<3:

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit()


    clean(
        sys.argv[1],
        sys.argv[2]
    )