# jianpu_fix_musicxml.py
# V13 SPLIT ENGINE
# 修正 jianpu_ly barcheck fail

import sys
from lxml import etree
from fractions import Fraction

DIVISIONS = 4
BEAT = 4
MEASURE_LEN = 16   # 4/4 = 16 divisions


def q_duration(d):
    """
    強制量化 duration
    """
    allowed = [
        1,2,4,8,16
    ]

    best = min(
        allowed,
        key=lambda x: abs(x-d)
    )

    return best


def remove_tag(root, tag):

    for e in root.xpath(f".//{{*}}{tag}"):
        parent=e.getparent()
        if parent is not None:
            parent.remove(e)


def fix_duration(root):

    for note in root.xpath(".//{{*}}note"):

        dur = note.find(".//{*}duration")

        if dur is None:
            continue

        try:
            value=int(dur.text)
        except:
            continue


        new=q_duration(value)

        dur.text=str(new)



def split_measure_notes(root):

    """
    重新按照4/4切割
    """

    notes=root.xpath(".//{{*}}note")


    pos=0


    for note in notes:

        dur=note.find(".//{*}duration")

        if dur is None:
            continue


        d=int(dur.text)


        # 超過小節
        if pos+d > MEASURE_LEN:

            remain=MEASURE_LEN-pos


            if remain>0:

                dur.text=str(remain)


            # 剩餘部分
            left=d-remain


            if left>0:

                clone=etree.fromstring(
                    etree.tostring(note)
                )

                clone.find(".//{*}duration").text=str(left)

                note.addnext(clone)


            pos=left


        else:

            pos+=d


        if pos>=MEASURE_LEN:
            pos=0



def rebuild_measures(root):

    """
    重新檢查小節長度
    """

    measures=root.xpath(".//{{*}}measure")


    for i,m in enumerate(measures,1):

        total=0

        for d in m.xpath(".//{{*}}duration"):

            try:
                total+=int(d.text)

            except:
                pass


        print(
            "Measure",
            i,
            total/4
        )


def main():

    if len(sys.argv)<3:

        print(
            "python jianpu_fix_musicxml.py input.musicxml output.musicxml"
        )
        return


    inp=sys.argv[1]
    out=sys.argv[2]


    tree=etree.parse(inp)

    root=tree.getroot()


    print("remove chords")
    remove_tag(root,"chord")


    print("remove beams")
    remove_tag(root,"beam")


    print("remove ties")
    remove_tag(root,"tie")


    print("quantize duration")

    fix_duration(root)


    print("split cross measure notes")

    split_measure_notes(root)


    print("FINAL CHECK")

    rebuild_measures(root)


    tree.write(
        out,
        encoding="UTF-8",
        xml_declaration=True
    )


    print("DONE")
    print(out)



if __name__=="__main__":
    main()