
VERSION = "V27"

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
# remove voices
# ==========================

print("remove voices")

for x in root.xpath(".//m:voice", namespaces=NS):
    p = x.getparent()
    if p is not None:
        p.remove(x)



# ==========================
# remove chords
# ==========================

print("remove chords")

for x in root.xpath(".//m:chord", namespaces=NS):
    p = x.getparent()
    if p is not None:
        p.remove(x)



# ==========================
# remove beams
# ==========================

print("remove beams")

for x in root.xpath(".//m:beam", namespaces=NS):
    p = x.getparent()
    if p is not None:
        p.remove(x)



# ==========================
# remove ties
# ==========================

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
# rebuild measure duration
# ==========================

print("rebuild measures")


for part in root.xpath(".//m:part", namespaces=NS):

    for measure in part.xpath("./m:measure", namespaces=NS):

        total = 0

        notes = measure.xpath("./m:note", namespaces=NS)

        for note in notes:

            dur = note.find(
                "m:duration",
                NS
            )

            if dur is None:
                continue

            try:
                value = int(dur.text)
            except:
                value = 1

            # 最小單位
            if value < 1:
                value = 1

            dur.text = str(value)

            total += value


        print(
            "Measure",
            measure.get("number"),
            total
        )


        # 超過小節
        if total > BAR_LENGTH:

            print(
                "FIX OVER MEASURE",
                measure.get("number"),
                total
            )


            remain = total - BAR_LENGTH

            for note in reversed(notes):

                if remain <= 0:
                    break


                dur = note.find(
                    "m:duration",
                    NS
                )

                if dur is None:
                    continue


                value = int(dur.text)


                if value > remain:

                    dur.text = str(
                        value - remain
                    )

                    remain = 0

                else:

                    remain -= value

                    dur.text = "1"



        # 不足補休止符

        total2 = 0

        for note in measure.xpath("./m:note", namespaces=NS):

            dur = note.find(
                "m:duration",
                NS
            )

            if dur is not None:

                total2 += int(dur.text)



        if total2 < BAR_LENGTH:

            missing = BAR_LENGTH - total2

            print(
                "ADD REST",
                measure.get("number"),
                missing
            )


            rest = etree.Element(
                "{%s}note" %
                NS["m"]
            )

            etree.SubElement(
                rest,
                "{%s}rest" %
                NS["m"]
            )

            d = etree.SubElement(
                rest,
                "{%s}duration" %
                NS["m"]
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
            "m:" + tag,
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