import sys
from lxml import etree


VERSION = "V27"


print("================")
print("CLEAN MUSICXML", VERSION)
print("================")


if len(sys.argv) < 3:
    print("Usage: python clean_musicxml_v27.py input.musicxml output.musicxml")
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


print("DIVISIONS", divisions)
print("BAR LENGTH", BAR_LENGTH)



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
# duration quantize
# ==========================

print("duration quantize")


for duration in root.xpath(".//m:duration", namespaces=NS):

    try:
        value = int(duration.text)

    except:
        continue


    # 四分音符16分割
    # 限制到合理值

    if value < 1:
        value = 1


    duration.text = str(value)



# ==========================
# rebuild measures
# ==========================

print("rebuild measures")


for part in root.xpath(".//m:part", namespaces=NS):

    measures = part.xpath("./m:measure", namespaces=NS)

    current = 0
    measure_no = 1


    for measure in measures:

        measure.set(
            "number",
            str(measure_no)
        )

        measure_no += 1

        current = 0


        for note in measure.xpath("./m:note", namespaces=NS):

            dur = note.find(
                "m:duration",
                NS
            )


            if dur is None:
                continue


            try:
                value = int(dur.text)

            except:
                continue


            current += value


        print(
            "Measure",
            measure.get("number"),
            current
        )



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
# write
# ==========================

print("FINAL WRITE")


tree.write(
    output_file,
    encoding="UTF-8",
    xml_declaration=True,
    pretty_print=True
)


print("DONE")
print(output_file)