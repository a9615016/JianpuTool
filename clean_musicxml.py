VERSION = "V30"

print("================")
print("CLEAN MUSICXML", VERSION)
print("================")

import sys
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
# remove unwanted notation
# ==========================

print("remove voices")

for x in root.xpath(".//m:voice", namespaces=NS):
    x.getparent().remove(x)


print("remove chords")

for x in root.xpath(".//m:chord", namespaces=NS):
    x.getparent().remove(x)


print("remove beams")

for x in root.xpath(".//m:beam", namespaces=NS):
    x.getparent().remove(x)


print("remove ties")

for x in root.xpath(".//m:tie", namespaces=NS):
    x.getparent().remove(x)



# ==========================
# force 4/4
# ==========================

print("force 4/4")

for time in root.xpath(".//m:time", namespaces=NS):

    beats = time.find("m:beats", NS)
    beat = time.find("m:beat-type", NS)

    if beats is not None:
        beats.text = "4"

    if beat is not None:
        beat.text = "4"



# ==========================
# split cross measure notes
# ==========================

print("split cross measure notes")


for part in root.xpath(".//m:part", namespaces=NS):

    carry = None


    measures = part.xpath("./m:measure", namespaces=NS)


    for measure in measures:


        notes = measure.xpath("./m:note", namespaces=NS)


        new_notes = []

        current = 0


        for note in notes:


            dur = note.find(
                "m:duration",
                NS
            )


            if dur is None:
                continue


            length = int(dur.text)



            # 超過小節切開

            while current + length > BAR_LENGTH:


                remain = BAR_LENGTH - current


                if remain > 0:

                    n = etree.fromstring(
                        etree.tostring(note)
                    )

                    n.find(
                        "m:duration",
                        NS
                    ).text = str(remain)


                    new_notes.append(n)



                length -= remain


                print(
                    "SPLIT NOTE",
                    measure.get("number"),
                    "remain",
                    length
                )


                current = BAR_LENGTH



            if length > 0:

                n = etree.fromstring(
                    etree.tostring(note)
                )

                n.find(
                    "m:duration",
                    NS
                ).text = str(length)


                new_notes.append(n)


                current += length



            # 到小節尾

            if current == BAR_LENGTH:

                current = 0



        # 清空舊 note

        for n in notes:
            measure.remove(n)


        # 寫回

        for n in new_notes:
            measure.append(n)



# ==========================
# fill empty measure
# ==========================

print("fill rests")


for measure in root.xpath(".//m:measure", namespaces=NS):

    total = 0

    for dur in measure.xpath(
        "./m:note/m:duration",
        namespaces=NS
    ):
        total += int(dur.text)


    if total < BAR_LENGTH:

        missing = BAR_LENGTH - total

        print(
            "ADD REST",
            measure.get("number"),
            missing
        )


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

        d.text = str(missing)


        measure.append(rest)



# ==========================
# clear notation
# ==========================

print("clear notation cache")


for note in root.xpath(".//m:note", namespaces=NS):

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


for measure in root.xpath(".//m:measure", namespaces=NS):

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



print("FINAL WRITE")


tree.write(
    output_file,
    encoding="UTF-8",
    xml_declaration=True,
    pretty_print=True
)


print("DONE")
print(output_file)