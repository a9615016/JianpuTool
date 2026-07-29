#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
jianpu_prepare_v2.py

MusicXML preprocessor for jianpu_ly

Fix:
- backup
- forward
- chord
- ties
- voice
- cross measure notes
- measure overflow
- fill rests
"""

import sys
from pathlib import Path
from lxml import etree


BEATS = 4


def create_rest(duration):

    note = etree.Element("note")

    etree.SubElement(
        note,
        "rest"
    )

    dur = etree.SubElement(
        note,
        "duration"
    )
    dur.text = str(duration)

    voice = etree.SubElement(
        note,
        "voice"
    )
    voice.text = "1"

    return note



def clone_note(note, duration):

    new_note = etree.fromstring(
        etree.tostring(note)
    )

    old = new_note.find("duration")

    if old is not None:
        old.text = str(duration)

    else:
        d = etree.SubElement(
            new_note,
            "duration"
        )
        d.text = str(duration)


    voice = new_note.find("voice")

    if voice is None:
        voice = etree.SubElement(
            new_note,
            "voice"
        )

    voice.text = "1"


    return new_note



def prepare(src, dst):

    print("LOAD", src)


    tree = etree.parse(src)
    root = tree.getroot()


    div_node = root.find(".//divisions")

    divisions = 16

    if div_node is not None:
        divisions = int(div_node.text)


    measure_length = divisions * BEATS


    print(
        "DIVISIONS",
        divisions,
        "MEASURE",
        measure_length
    )


    # ------------------------
    # remove global unwanted
    # ------------------------

    for x in root.xpath(".//backup"):
        x.getparent().remove(x)

    for x in root.xpath(".//forward"):
        x.getparent().remove(x)


    for x in root.xpath(".//tie"):
        x.getparent().remove(x)


    for x in root.xpath(".//notations"):
        x.getparent().remove(x)



    # ------------------------
    # measures
    # ------------------------

    for measure in root.xpath(".//measure"):

        number = measure.get("number")

        print(
            "PROCESS MEASURE",
            number
        )


        new_children=[]

        current=0


        for item in list(measure):

            tag = etree.QName(item).localname


            if tag != "note":
                continue


            # remove chord
            chord=item.find("chord")

            if chord is not None:
                item.remove(chord)


            # force voice

            voice=item.find("voice")

            if voice is None:
                voice=etree.SubElement(
                    item,
                    "voice"
                )

            voice.text="1"


            dur=item.find("duration")

            if dur is None:
                continue


            duration=int(dur.text)


            # ---------------------
            # split overflow note
            # ---------------------

            while current + duration > measure_length:

                remain = measure_length-current


                if remain > 0:

                    print(
                        "split note",
                        number,
                        "remain",
                        remain
                    )


                    part=clone_note(
                        item,
                        remain
                    )

                    new_children.append(part)


                duration -= remain

                current = measure_length


                break



            if current < measure_length and duration>0:


                if current+duration <= measure_length:

                    part=clone_note(
                        item,
                        duration
                    )

                    new_children.append(part)

                    current += duration



        # clear old notes

        for item in list(measure):

            if etree.QName(item).localname=="note":
                measure.remove(item)



        # write notes back

        for n in new_children:

            measure.append(n)



        # fill rest

        if current < measure_length:

            missing=measure_length-current

            print(
                "fill rest",
                number,
                missing
            )

            measure.append(
                create_rest(missing)
            )

            current += missing



        print(
            "MEASURE",
            number,
            current/divisions
        )


    tree.write(
        dst,
        encoding="UTF-8",
        xml_declaration=True
    )


    print()
    print("DONE")
    print(dst)



if __name__=="__main__":


    if len(sys.argv)<3:

        print(
            "usage:"
        )

        print(
            "python jianpu_prepare_v2.py input.musicxml output.musicxml"
        )

        sys.exit(1)


    prepare(
        sys.argv[1],
        sys.argv[2]
    )