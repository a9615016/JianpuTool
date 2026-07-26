# clean_musicxml.py
# CLEAN VERSION 20260726 V14
# force measure split version

import sys
import xml.etree.ElementTree as ET
import copy


TARGET_DIVISIONS = 16
BEATS_PER_BAR = 4
BAR_LENGTH = TARGET_DIVISIONS * BEATS_PER_BAR


def tag(x):
    return x.split("}")[-1]


def make_element(name, text=None):
    e = ET.Element(name)
    if text:
        e.text = str(text)
    return e


def quantize_duration(d):

    values = [
        1,2,4,8,16,32
    ]

    return min(
        values,
        key=lambda x:abs(x-d)
    )


def clean_measure(measure):

    new_notes = []

    current = 0


    for note in list(measure):

        if tag(note.tag) != "note":
            continue


        duration_node = note.find(
            "{*}duration"
        )


        if duration_node is None:
            continue


        duration = int(duration_node.text)


        # quantize
        duration = quantize_duration(duration)


        # split across bar
        while current + duration > BAR_LENGTH:

            remain = BAR_LENGTH - current


            if remain > 0:

                part = copy.deepcopy(note)

                part.find(
                    "{*}duration"
                ).text = str(remain)

                new_notes.append(part)



            # new bar marker
            current = 0


            duration -= remain


            if duration <= 0:
                break



        if duration > 0:

            part = copy.deepcopy(note)

            part.find(
                "{*}duration"
            ).text = str(duration)

            new_notes.append(part)

            current += duration



        # bar full
        if current == BAR_LENGTH:

            current = 0



    # rebuild measure

    for child in list(measure):
        measure.remove(child)


    for n in new_notes:
        measure.append(n)



    # fill missing duration

    total = 0

    for n in new_notes:

        d=n.find("{*}duration")

        if d is not None:
            total += int(d.text)



    if total < BAR_LENGTH:

        rest = ET.Element(
            "note"
        )

        ET.SubElement(
            rest,
            "rest"
        )

        ET.SubElement(
            rest,
            "duration"
        ).text=str(
            BAR_LENGTH-total
        )

        measure.append(rest)



def clean_file(src,dst):

    print(
        "CLEAN VERSION 20260726 V14"
    )

    print(
        "input:",
        src
    )


    tree=ET.parse(src)

    root=tree.getroot()


    # remove voices/chords/grace

    for elem in root.iter():

        if tag(elem.tag)=="voice":

            elem.clear()


        if tag(elem.tag)=="chord":

            elem.clear()


        if tag(elem.tag)=="grace":

            elem.clear()



    # set divisions

    for div in root.iter():

        if tag(div.tag)=="divisions":

            div.text=str(
                TARGET_DIVISIONS
            )


    print(
        "repair measures"
    )


    for measure in root.iter():

        if tag(measure.tag)=="measure":

            clean_measure(
                measure
            )


    print(
        "final cleanup"
    )


    tree.write(
        dst,
        encoding="utf-8",
        xml_declaration=True
    )


    print(
        "done:",
        dst
    )



if __name__=="__main__":

    if len(sys.argv)<3:

        print(
            "usage: python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit(1)


    clean_file(
        sys.argv[1],
        sys.argv[2]
    )