# clean_musicxml.py
# V70
# jianpu_ly XML HARD COMPATIBLE


from lxml import etree
from fractions import Fraction
import sys


VERSION = "CLEAN MUSICXML V70"


GRID = {
    1: 1,
    2: 2,
    4: 4,
    8: 8,
    16:16
}


def quantize_duration(x):

    x=int(x)

    best=min(
        GRID.keys(),
        key=lambda k:abs(x-k)
    )

    return str(GRID[best])



def clean_xml(inp,out):


    print(VERSION)


    tree=etree.parse(inp)

    root=tree.getroot()


    ns={
        "m":"http://www.musicxml.org/ns/musicxml",
    }


    # namespace fallback

    if not root.nsmap.get(None):

        ns={
            "m":root.nsmap.get(None)
        }



    # =====================
    # time signature
    # =====================

    for time in root.xpath(".//m:time",namespaces=ns):

        nums=time.xpath(
            "./m:numerator",
            namespaces=ns
        )

        dens=time.xpath(
            "./m:denominator",
            namespaces=ns
        )


        if nums:
            nums[0].text="4"

        if dens:
            dens[0].text="4"



    # =====================
    # remove backup forward
    # =====================

    for tag in [
        "backup",
        "forward"
    ]:

        for e in root.xpath(
            ".//m:"+tag,
            namespaces=ns
        ):

            parent=e.getparent()

            if parent is not None:
                parent.remove(e)



    # =====================
    # notes
    # =====================


    for note in root.xpath(
        ".//m:note",
        namespaces=ns
    ):


        # voice

        for v in note.xpath(
            "./m:voice",
            namespaces=ns
        ):

            v.text="1"



        # duration

        for d in note.xpath(
            "./m:duration",
            namespaces=ns
        ):


            try:

                d.text=quantize_duration(
                    d.text
                )

            except:

                d.text="1"



        # remove beam

        for b in note.xpath(
            "./m:beam",
            namespaces=ns
        ):

            note.remove(b)



        # remove tie

        for t in note.xpath(
            "./m:tie",
            namespaces=ns
        ):

            note.remove(t)



        # remove notation

        for n in note.xpath(
            "./m:notations",
            namespaces=ns
        ):

            note.remove(n)



    # =====================
    # remove invalid tempo
    # =====================


    for tempo in root.xpath(
        ".//m:metronome",
        namespaces=ns
    ):

        parent=tempo.getparent()

        if parent is not None:

            parent.remove(tempo)



    tree.write(
        out,
        encoding="UTF-8",
        xml_declaration=True
    )


    print("DONE")
    print(out)



if __name__=="__main__":


    inp=sys.argv[1]

    out="clean.musicxml"


    if len(sys.argv)>2:

        out=sys.argv[2]


    clean_xml(
        inp,
        out
    )