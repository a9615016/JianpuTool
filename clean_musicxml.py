import sys
import os
from lxml import etree
from music21 import converter, meter, stream


print("==============================")
print("CLEAN VERSION 20260727")
print("==============================")


if len(sys.argv) < 2:
    print(
        "Usage: python clean_musicxml.py input.musicxml [output.musicxml]"
    )
    sys.exit(1)


input_file = sys.argv[1]


if len(sys.argv) >= 3:
    output_file = sys.argv[2]
else:
    output_file = os.path.splitext(input_file)[0] + "_clean.musicxml"



# =================================
# XML LOW LEVEL CLEAN
# =================================

print("XML CLEAN START")


tree = etree.parse(input_file)
root = tree.getroot()



# remove chord tags
print("remove chords")

for e in root.findall(".//chord"):
    parent = e.getparent()
    if parent is not None:
        parent.remove(e)



# remove beams

print("remove beams")

for e in root.findall(".//beam"):
    parent = e.getparent()
    if parent is not None:
        parent.remove(e)



# remove ties

print("remove ties")

for e in root.findall(".//tie"):
    parent = e.getparent()
    if parent is not None:
        parent.remove(e)

for e in root.findall(".//tied"):
    parent = e.getparent()
    if parent is not None:
        parent.remove(e)



# remove voice
print("remove voices")

for e in root.findall(".//voice"):
    parent = e.getparent()
    if parent is not None:
        parent.remove(e)



# remove backup

print("remove backups")

for e in root.findall(".//backup"):
    parent = e.getparent()
    if parent is not None:
        parent.remove(e)



# remove forward

print("remove forwards")

for e in root.findall(".//forward"):
    parent = e.getparent()
    if parent is not None:
        parent.remove(e)



tmp_xml = input_file.replace(
    ".musicxml",
    "_xmlclean.musicxml"
)


tree.write(
    tmp_xml,
    encoding="UTF-8",
    xml_declaration=True
)



# =================================
# MUSIC21 CLEAN
# =================================

print("LOAD MUSICXML")

score = converter.parse(tmp_xml)



# force 4/4

print("force 4/4")

for part in score.parts:

    part.insert(
        0,
        meter.TimeSignature("4/4")
    )



# quantize duration

print("duration quantize")

for part in score.parts:

    for n in part.recurse().notesAndRests:

        q = n.duration.quarterLength

        # 四分音符網格
        n.duration.quarterLength = round(
            q * 4
        ) / 4



# rebuild measures

print("rebuild measures")

score.makeMeasures(
    inPlace=True
)



# split cross measure notes

print("split cross measure notes")

score.makeNotation(
    inPlace=True
)



# fill empty measure

print("fill measure rest")

for part in score.parts:

    for m in part.getElementsByClass(
        stream.Measure
    ):

        total = sum(
            n.duration.quarterLength
            for n in m.notesAndRests
        )


        if total < 4:

            r = stream.Rest()

            r.duration.quarterLength = (
                4-total
            )

            m.append(r)



# rebuild again

print("rebuild measures")

score.makeMeasures(
    inPlace=True
)



# =================================
# FINAL CHECK
# =================================

print("==============================")
print("FINAL CHECK")
print("==============================")


error = False


for part in score.parts:

    for m in part.getElementsByClass(
        stream.Measure
    ):

        total = sum(
            n.duration.quarterLength
            for n in m.notesAndRests
        )


        print(
            "Measure",
            m.number,
            total
        )


        if abs(total-4.0)>0.001:

            print(
                "ERROR Measure",
                m.number
            )

            error=True



if error:

    print(
        "MEASURE ERROR STOP"
    )

    sys.exit(1)



print(
    "ALL MEASURES SAFE"
)



# =================================
# WRITE
# =================================

print("FINAL WRITE")


score.write(
    "musicxml",
    fp=output_file
)


print(
    "DONE"
)

print(
    output_file
)