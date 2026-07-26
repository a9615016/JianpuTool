# clean_musicxml.py
# CLEAN VERSION 20260726 V11
# quantize + repair measure overflow


import sys
import os
import xml.etree.ElementTree as ET


NS = {
    "m": "http://www.musicxml.org/ns/musicxml"
}

ET.register_namespace("", NS["m"])


STEP = 16   # divisions per quarter
BAR = 64    # 4/4


def qname(tag):
    return f"{{{NS['m']}}}{tag}"


def quantize_duration(value):

    try:
        d = int(value)
    except:
        return STEP

    # 量化到 16th
    allowed = [
        1,
        2,
        4,
        8,
        16,
        32,
        64
    ]

    nearest = min(
        allowed,
        key=lambda x: abs(x-d)
    )

    return nearest



def clean_musicxml(input_file, output_file):

    print("CLEAN VERSION 20260726 V11")
    print("input:", input_file)

    tree = ET.parse(input_file)
    root = tree.getroot()


    print("remove voices")
    for voice in root.findall(".//" + qname("voice")):
        voice.text = "1"


    print("remove chords")
    for chord in root.findall(".//" + qname("chord")):
        parent = None


    print("remove grace")
    for grace in root.findall(".//" + qname("grace")):
        parent = None


    print("quantize duration")


    for duration in root.findall(".//" + qname("duration")):

        new = quantize_duration(duration.text)

        duration.text = str(new)



    print("repair measures")


    measures = root.findall(
        ".//" + qname("measure")
    )


    for idx, measure in enumerate(measures):

        total = 0

        durations = []

        for note in measure.findall(
            qname("note")
        ):

            d = note.find(
                qname("duration")
            )

            if d is not None:

                value = int(d.text)

                total += value

                durations.append(
                    (d,value)
                )


        # 超過小節
        if total > BAR:

            print(
                "fix overflow measure",
                idx+1,
                total
            )


            overflow = total - BAR


            for d,value in reversed(durations):

                if overflow <= 0:
                    break


                new = value - overflow


                if new <= 0:
                    new = 1


                overflow -= (
                    value-new
                )


                d.text=str(new)



        # 不足補休止符

        elif total < BAR:

            remain = BAR-total


            print(
                "fill rest",
                idx+1,
                remain
            )


            note = ET.Element(
                qname("note")
            )

            rest = ET.SubElement(
                note,
                qname("rest")
            )


            duration = ET.SubElement(
                note,
                qname("duration")
            )

            duration.text=str(remain)


            measure.append(note)



    print("final cleanup")


    # 移除空 voice
    for elem in root.iter():

        for child in list(elem):

            if child.tag == qname("voice"):
                elem.remove(child)



    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True
    )


    print("done:", output_file)



if __name__ == "__main__":

    if len(sys.argv)<2:

        print(
            "python clean_musicxml.py input.musicxml [output.musicxml]"
        )

        sys.exit()


    input_file=sys.argv[1]


    if len(sys.argv)>=3:
        output_file=sys.argv[2]

    else:
        base=os.path.splitext(input_file)[0]
        output_file=base+"_clean.musicxml"



    clean_musicxml(
        input_file,
        output_file
    )