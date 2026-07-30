import sys
from pathlib import Path
from lxml import etree

src = sys.argv[1]
dst = sys.argv[2]

tree = etree.parse(src)

root = tree.getroot()

# 限制 MusicXML octave
for pitch in root.xpath(".//pitch"):
    octave = pitch.find("octave")

    if octave is not None:
        try:
            value = int(octave.text)

            if value < 2:
                octave.text = "2"

            if value > 8:
                octave.text = "8"

        except:
            pass

tree.write(
    dst,
    encoding="UTF-8",
    xml_declaration=True
)

print("OCTAVE FIX DONE")