import sys
from lxml import etree


VERSION = "V24_TEST"


print("================")
print("CLEAN MUSICXML", VERSION)
print("================")


if len(sys.argv) < 3:
    print("Usage:")
    print("python clean_musicxml_v24_test.py input.musicxml output.musicxml")
    sys.exit(1)


input_file = sys.argv[1]
output_file = sys.argv[2]


print("read")

tree = etree.parse(input_file)
root = tree.getroot()


# namespace
ns = {
    "m": "http://www.musicxml.org/ns/musicxml"
}


print("remove voices")

for voice in root.xpath(".//m:voice", namespaces=ns):
    parent = voice.getparent()
    if parent is not None:
        parent.remove(voice)


print("remove chords")

for chord in root.xpath(".//m:chord", namespaces=ns):
    parent = chord.getparent()
    if parent is not None:
        parent.remove(chord)


print("remove beams")

for beam in root.xpath(".//m:beam", namespaces=ns):
    parent = beam.getparent()
    if parent is not None:
        parent.remove(beam)


print("remove ties")

for tie in root.xpath(".//m:tie", namespaces=ns):
    parent = tie.getparent()
    if parent is not None:
        parent.remove(tie)


print("force 4/4")

for time in root.xpath(".//m:time", namespaces=ns):

    beats = time.find("m:beats", ns)
    beat_type = time.find("m:beat-type", ns)

    if beats is not None:
        beats.text = "4"

    if beat_type is not None:
        beat_type.text = "4"



print("duration quantize")

# V24 保守版
# 不改音符，只清除危險 notation

for note in root.xpath(".//m:note", namespaces=ns):

    for tag in [
        "notations",
        "articulations",
        "ornaments"
    ]:
        element = note.find(
            "m:"+tag,
            ns
        )

        if element is not None:
            note.remove(element)



print("clear notation cache")


tree.write(
    output_file,
    encoding="UTF-8",
    xml_declaration=True,
    pretty_print=True
)


print("FINAL WRITE")
print("DONE")
print(output_file)