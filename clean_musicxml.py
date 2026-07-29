# clean_musicxml.py
# V27 MUSICXML QUANTIZER FOR JIANPU_LY

import sys
import xml.etree.ElementTree as ET
from fractions import Fraction


DIVISIONS = 16
BEATS_PER_MEASURE = 4


def snap(value):
    """
    四分音符網格量化
    """
    step = Fraction(1, 16)

    return float(
        round(
            Fraction(value) / step
        ) * step
    )


def duration_snap(d):

    allowed = [
        0.25,   #16分
        0.5,    #8分
        1.0,    #4分
        2.0,    #2分
        4.0     #全音符
    ]

    return min(
        allowed,
        key=lambda x: abs(x-d)
    )



def clean(input_file, output_file):

    print("================")
    print("CLEAN MUSICXML V27 QUANTIZER")
    print("================")


    tree = ET.parse(input_file)
    root = tree.getroot()


    ns = {
        "m":
        "http://www.musicxml.org"
    }


    # ----------------------
    # 強制4/4
    # ----------------------

    for time in root.iter():

        if time.tag.endswith("time"):

            for child in list(time):

                if child.tag.endswith("beats"):
                    child.text="4"

                if child.tag.endswith("beat-type"):
                    child.text="4"



    # ----------------------
    # 修正 duration
    # ----------------------

    for dur in root.iter():

        if dur.tag.endswith("duration"):

            try:

                old = int(dur.text)

                beats = old / DIVISIONS

                new = duration_snap(beats)


                dur.text=str(
                    int(new * DIVISIONS)
                )


            except:

                pass



    # ----------------------
    # 移除危險元素
    # ----------------------

    remove_tags=[
        "voice",
        "chord",
        "tie",
        "beam"
    ]


    for parent in root.iter():

        for child in list(parent):

            name = child.tag.split("}")[-1]

            if name in remove_tags:
                parent.remove(child)



    # ----------------------
    # 檢查小節
    # ----------------------

    print()
    print("FINAL CHECK")


    measure_no=1

    for measure in root.iter():

        if measure.tag.endswith("measure"):

            total=0

            for d in measure.iter():

                if d.tag.endswith("duration"):

                    total += int(d.text)/DIVISIONS


            print(
                "Measure",
                measure_no,
                total
            )


            measure_no+=1



    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True
    )


    print()
    print("DONE")
    print(output_file)



if __name__=="__main__":

    clean(
        sys.argv[1],
        sys.argv[2]
    )