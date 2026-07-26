import sys
import os
import xml.etree.ElementTree as ET
from fractions import Fraction


VERSION = "CLEAN VERSION 20260726 V13"


def log(x):
    print(x)


def quantize_duration(duration, divisions):
    """
    四捨五入到 16 分音符
    """
    step = divisions // 4

    if step <= 0:
        return duration

    q = round(duration / step) * step

    if q <= 0:
        q = step

    return q


def clean_musicxml(input_file, output_file):

    log(VERSION)
    log("input: " + input_file)

    tree = ET.parse(input_file)
    root = tree.getroot()


    divisions = 16

    div_node = root.find(".//divisions")
    if div_node is not None:
        divisions = int(div_node.text)


    log("remove voices")
    log("remove chords")
    log("remove grace")

    # 移除 voice
    for voice in root.findall(".//voice"):
        parent = None
        for p in root.iter():
            if voice in list(p):
                parent = p
                break

        if parent is not None:
            parent.remove(voice)


    # 移除 chord 標記
    for chord in root.findall(".//chord"):
        parent = None
        for p in root.iter():
            if chord in list(p):
                parent=p
                break

        if parent:
            parent.remove(chord)


    log("quantize duration")

    # 所有 note duration 量化
    for dur in root.findall(".//duration"):

        try:
            value=int(dur.text)

            value=quantize_duration(
                value,
                divisions
            )

            dur.text=str(value)

        except:
            pass



    log("repair measures")

    measure_list = root.findall(".//measure")


    for measure in measure_list:

        notes = measure.findall(".//note")

        total = 0

        for note in notes:

            dur = note.find("duration")

            if dur is not None:
                try:
                    total += int(dur.text)
                except:
                    pass


        target = divisions * 4


        # 超過小節
        if total > target:

            overflow = total-target


            for note in reversed(notes):

                dur=note.find("duration")

                if dur is None:
                    continue

                d=int(dur.text)


                if d > overflow:

                    dur.text=str(d-overflow)
                    overflow=0
                    break

                else:

                    dur.text=str(divisions//4)
                    overflow-=d


                if overflow<=0:
                    break



        # 不足補休止符

        if total < target:

            rest_time = target-total

            rest = ET.Element("note")

            ET.SubElement(rest,"rest")

            ET.SubElement(
                rest,
                "duration"
            ).text=str(rest_time)


            measure.append(rest)



    log("final cleanup")


    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True
    )


    log("done:")
    log(output_file)



if __name__=="__main__":

    if len(sys.argv)<2:

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        exit()


    input_file=sys.argv[1]


    if len(sys.argv)>=3:
        output_file=sys.argv[2]

    else:
        output_file=input_file.replace(
            ".musicxml",
            "_clean.musicxml"
        )


    clean_musicxml(
        input_file,
        output_file
    )