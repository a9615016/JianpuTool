# jianpu_fix_musicxml.py
# V11 FINAL
# Full rebuild 4/4 + duration quantize

import sys
import xml.etree.ElementTree as ET
from fractions import Fraction

NS = {
    "m": "http://www.musicxml.org/ns/musicxml"
}

ET.register_namespace("", NS["m"])


STEP = 16        # divisions
BAR = 64         # 4/4 = 16*4


def q_duration(d):

    # MusicXML duration -> quantized 16th

    x = float(d)

    table = [
        (0.25,4),
        (0.5,8),
        (0.75,12),
        (1,16),
        (1.5,24),
        (2,32),
        (3,48),
        (4,64)
    ]

    best = min(
        table,
        key=lambda a: abs(a[0]-x)
    )

    return best[1]


def remove_tag(parent, tag):

    for e in list(parent):
        if e.tag.endswith(tag):
            parent.remove(e)


def get_notes(measure):

    result=[]

    for n in measure.findall(".//{*}note"):

        if n.find("{*}rest") is not None:
            continue

        d=n.find("{*}duration")

        if d is None:
            continue

        result.append(n)

    return result



def rebuild(input_file, output_file):

    tree=ET.parse(input_file)
    root=tree.getroot()


    # divisions 全部改16

    for div in root.findall(".//{*}divisions"):
        div.text=str(STEP)



    # 清理

    for e in root.findall(".//{*}voice"):
        e.text="1"


    for e in root.findall(".//{*}beam"):
        for p in list(e):
            e.remove(p)


    for e in root.findall(".//{*}tie"):
        parent=None


    # 取得第一個 part

    part=root.find(".//{*}part")

    old=list(part.findall("{*}measure"))


    notes=[]


    for m in old:

        for n in get_notes(m):

            d=n.find("{*}duration")

            if d is not None:

                d.text=str(
                    q_duration(d.text)
                )

                notes.append(n)



    # 刪除全部小節

    for m in old:
        part.remove(m)



    # 重建4/4

    bar=[]

    total=0

    number=1


    for n in notes:

        d=int(
            n.find("{*}duration").text
        )


        if total+d > BAR:

            # 補休止

            rest=ET.Element(
                "note"
            )

            ET.SubElement(
                rest,
                "rest"
            )

            dur=ET.SubElement(
                rest,
                "duration"
            )

            dur.text=str(
                BAR-total
            )

            bar.append(rest)


            measure=ET.Element(
                "measure",
                {"number":str(number)}
            )

            for x in bar:
                measure.append(x)


            part.append(measure)


            number+=1
            bar=[]
            total=0



        bar.append(n)
        total+=d



    # 最後一小節補滿

    if bar:

        if total < BAR:

            rest=ET.Element("note")

            ET.SubElement(
                rest,
                "rest"
            )

            dur=ET.SubElement(
                rest,
                "duration"
            )

            dur.text=str(
                BAR-total
            )

            bar.append(rest)


        measure=ET.Element(
            "measure",
            {"number":str(number)}
        )

        for x in bar:
            measure.append(x)

        part.append(measure)



    # 最終檢查

    print("================")
    print("JIANPU FIX MUSICXML V11 FINAL")
    print("================")


    for m in part.findall("{*}measure"):

        s=0

        for d in m.findall(".//{*}duration"):
            s+=int(d.text)


        print(
            "Measure",
            m.attrib["number"],
            s/STEP
        )


    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True
    )


    print("DONE")
    print(output_file)



if __name__=="__main__":

    if len(sys.argv)<3:
        print(
            "python jianpu_fix_musicxml.py input.musicxml output.musicxml"
        )
        sys.exit()


    rebuild(
        sys.argv[1],
        sys.argv[2]
    )