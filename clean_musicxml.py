VERSION = "V28"

print("================")
print("CLEAN MUSICXML", VERSION)
print("================")

import sys
import copy
from lxml import etree


if len(sys.argv) < 3:
    print("Usage: python clean_musicxml.py input.musicxml output.musicxml")
    sys.exit(1)


input_file = sys.argv[1]
output_file = sys.argv[2]


NS = {
    "m": "http://www.musicxml.org/ns/musicxml"
}


tree = etree.parse(input_file)
root = tree.getroot()


# ==========================
# divisions
# ==========================

divisions = 16

div = root.find(".//m:divisions", NS)

if div is not None:
    divisions = int(div.text)


BAR_LENGTH = divisions * 4


print("DIVISIONS =", divisions)
print("BAR_LENGTH =", BAR_LENGTH)



# ==========================
# remove notation
# ==========================

print("remove voices")

for x in root.xpath(".//m:voice", namespaces=NS):
    p = x.getparent()
    if p is not None:
        p.remove(x)


print("remove chords")

for x in root.xpath(".//m:chord", namespaces=NS):
    p = x.getparent()
    if p is not None:
        p.remove(x)


print("remove beams")

for x in root.xpath(".//m:beam", namespaces=NS):
    p = x.getparent()
    if p is not None:
        p.remove(x)


print("remove ties")

for x in root.xpath(".//m:tie", namespaces=NS):
    p = x.getparent()
    if p is not None:
        p.remove(x)



# ==========================
# force 4/4
# ==========================

print("force 4/4")


for time in root.xpath(".//m:time", namespaces=NS):

    beats = time.find("m:beats", NS)
    beat_type = time.find("m:beat-type", NS)

    if beats is not None:
        beats.text = "4"

    if beat_type is not None:
        beat_type.text = "4"



# ==========================
# duration quantize
# ==========================

print("quantize duration")


def quantize(value):

    allowed = [
        64,
        32,
        16,
        8,
        4,
        2,
        1
    ]

    return min(
        allowed,
        key=lambda x: abs(x-value)
    )



for dur in root.xpath(
    ".//m:duration",
    namespaces=NS
):

    try:
        value = int(dur.text)
    except:
        value = 1


    if value < 1:
        value = 1


    dur.text = str(
        quantize(value)
    )



# ==========================
# rebuild measures
# ==========================

print("rebuild measures")


for part in root.xpath(".//m:part", namespaces=NS):

    carry = None


    measures = part.xpath(
        "./m:measure",
        namespaces=NS
    )


    for measure in measures:


        notes = measure.xpath(
            "./m:note",
            namespaces=NS
        )


        new_notes = []

        total = 0


        for note in notes:


            dur = note.find(
                "m:duration",
                NS
            )

            if dur is None:
                continue


            value = int(
                dur.text
            )


            while value > 0:


                remain = BAR_LENGTH - total


                if value <= remain:

                    dur.text = str(value)

                    new_notes.append(note)

                    total += value

                    value = 0


                else:


                    # split note

                    first = copy.deepcopy(note)

                    first_dur = first.find(
                        "m:duration",
                        NS
                    )

                    first_dur.text = str(remain)


                    new_notes.append(first)


                    value -= remain


                    total = BAR_LENGTH



                    # create carry

                    carry = copy.deepcopy(note)

                    carry_dur = carry.find(
                        "m:duration",
                        NS
                    )

                    carry_dur.text = str(value)



        # clear old notes

        for n in notes:
            measure.remove(n)


        for n in new_notes:
            measure.append(n)



        # fill rest

        if total < BAR_LENGTH:

            rest = etree.Element(
                "{%s}note" % NS["m"]
            )

            etree.SubElement(
                rest,
                "{%s}rest" % NS["m"]
            )


            d = etree.SubElement(
                rest,
                "{%s}duration" % NS["m"]
            )

            d.text = str(
                BAR_LENGTH-total
            )


            measure.append(rest)



# ==========================
# clear notation
# ==========================

print("clear notation")


for note in root.xpath(
    ".//m:note",
    namespaces=NS
):

    for tag in [
        "notations",
        "articulations",
        "ornaments"
    ]:

        obj = note.find(
            "m:"+tag,
            NS
        )

        if obj is not None:
            note.remove(obj)



# ==========================
# FINAL CHECK
# ==========================

print("FINAL CHECK")


for measure in root.xpath(
    ".//m:measure",
    namespaces=NS
):

    total = 0


    for dur in measure.xpath(
        "./m:note/m:duration",
        namespaces=NS
    ):

        total += int(dur.text)


    print(
        "Measure",
        measure.get("number"),
        total
    )


    if total != BAR_LENGTH:
        print(
            "WARNING BAD BAR",
            measure.get("number"),
            total
        )



print("FINAL WRITE")


tree.write(
    output_file,
    encoding="UTF-8",
    xml_declaration=True,
    pretty_print=True
)


print("DONE")
print(output_file)