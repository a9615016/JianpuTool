# CLEAN MUSICXML V34 FIX
# JianpuTool MVP

from lxml import etree
from copy import deepcopy
import sys


if len(sys.argv) < 3:
    print(
        "python clean_musicxml.py input.musicxml output.musicxml"
    )
    raise SystemExit


inp = sys.argv[1]
out = sys.argv[2]


print("================")
print("CLEAN MUSICXML V34 FIX")
print("================")


tree = etree.parse(inp)
root = tree.getroot()


# ==========================
# Remove notation
# ==========================

for tag in (
    "chord",
    "beam",
    "tie",
    "backup",
    "forward",
    "voice"
):

    for e in root.xpath(f".//{tag}"):

        p = e.getparent()

        if p is not None:
            p.remove(e)



# ==========================
# Assume divisions = 16
# 4/4 bar = 64
# ==========================

BAR = 64


measures = root.xpath(".//measure")


for measure in measures:

    cur = 0

    notes = list(
        measure.xpath("./note")
    )


    for note in notes:

        duration = note.find("duration")


        if duration is None:
            continue


        try:
            length = int(duration.text)

        except:
            continue



        # split note crossing bar

        if cur + length > BAR:

            first = BAR - cur

            overflow = length - first


            if first > 0:

                duration.text = str(first)


            second = deepcopy(note)


            second_duration = second.find(
                "duration"
            )


            if second_duration is not None:
                second_duration.text = str(overflow)



            # find next measure

            next_measure = measure.getnext()


            while next_measure is not None:

                if (
                    isinstance(
                        next_measure.tag,
                        str
                    )
                    and
                    etree.QName(
                        next_measure
                    ).localname
                    ==
                    "measure"
                ):
                    break


                next_measure = next_measure.getnext()



            if next_measure is None:

                next_measure = etree.Element(
                    "measure"
                )

                next_measure.set(
                    "number",
                    str(
                        int(
                            measure.get(
                                "number",
                                "0"
                            )
                        )
                        + 1
                    )
                )


                measure.addnext(
                    next_measure
                )



            next_measure.insert(
                0,
                second
            )


            cur = overflow


        else:

            cur += length



# ==========================
# Write
# ==========================

tree.write(
    out,
    encoding="utf-8",
    xml_declaration=True
)


print("================")
print("DONE")
print(out)
print("================")
