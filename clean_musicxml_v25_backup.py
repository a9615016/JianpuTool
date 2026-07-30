import sys
from lxml import etree


VERSION = "V26"


print("================")
print("CLEAN MUSICXML", VERSION)
print("================")


if len(sys.argv) < 3:
    print(
        "Usage: python clean_musicxml_v26.py input.musicxml output.musicxml"
    )
    sys.exit(1)


input_file = sys.argv[1]
output_file = sys.argv[2]


ns = {
    "m": "http://www.musicxml.org/ns/musicxml"
}


print("read")

tree = etree.parse(input_file)
root = tree.getroot()


# ==========================
# remove voices
# ==========================

print("remove voices")

for x in root.xpath(".//m:voice", namespaces=ns):
    parent = x.getparent()
    if parent is not None:
        parent.remove(x)


# ==========================
# remove chords
# ==========================

print("remove chords")

for x in root.xpath(".//m:chord", namespaces=ns):
    parent = x.getparent()
    if parent is not None:
        parent.remove(x)


# ==========================
# remove beams
# ==========================

print("remove beams")

for x in root.xpath(".//m:beam", namespaces=ns):
    parent = x.getparent()
    if parent is not None:
        parent.remove(x)


# ==========================
# remove ties
# ==========================

print("remove ties")

for x in root.xpath(".//m:tie", namespaces=ns):
    parent = x.getparent()
    if parent is not None:
        parent.remove(x)



# ==========================
# force 4/4
# ==========================

print("force 4/4")

for time in root.xpath(".//m:time", namespaces=ns):

    beats = time.find("m:beats", ns)
    beat_type = time.find("m:beat-type", ns)

    if beats is not None:
        beats.text = "4"

    if beat_type is not None:
        beat_type.text = "4"



# ==========================
# octave clamp
# ==========================

print("octave clamp")


# jianpu_ly 可接受:
# ,,,  ,,,  ,,  ,  ''
# 不接受 ,,,,

for note in root.xpath(".//m:note", namespaces=ns):

    pitch = note.find("m:pitch", ns)

    if pitch is None:
        continue


    octave = pitch.find(
        "m:octave",
        ns
    )

    if octave is None:
        continue


    try:
        value = int(octave.text)

    except:
        continue


    # 太低音限制
    if value < 2:

        print(
            "clamp octave",
            value,
            "-> 2"
        )

        octave.text = "2"



# ==========================
# clear notation
# ==========================

print("clear notation cache")


for note in root.xpath(".//m:note", namespaces=ns):

    for tag in [
        "notations",
        "articulations",
        "ornaments"
    ]:

        obj = note.find(
            "m:" + tag,
            ns
        )

        if obj is not None:
            note.remove(obj)



print("FINAL WRITE")


tree.write(
    output_file,
    encoding="UTF-8",
    xml_declaration=True,
    pretty_print=True
)


print("DONE")
print(output_file)