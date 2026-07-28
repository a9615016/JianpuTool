import sys
import xml.etree.ElementTree as ET
from fractions import Fraction

print("================")
print("CLEAN MUSICXML V65")
print("ABSOLUTE QUANTIZE ENGINE")
print("================")


INPUT = sys.argv[1]
OUTPUT = sys.argv[2] if len(sys.argv)>2 else "clean.musicxml"


tree = ET.parse(INPUT)
root = tree.getroot()

ns = {"m":"http://www.musicxml.org/ns/musicxml"}

ET.register_namespace("", "http://www.musicxml.org/ns/musicxml")


# -------------------------
# force divisions
# -------------------------

for attr in root.findall(".//attributes"):

    div = attr.find("divisions")

    if div is not None:
        div.text="16"



# -------------------------
# quantize table
# -------------------------

GRID = [
    (64,64),
    (48,64),
    (32,32),
    (24,32),
    (16,16),
    (12,16),
    (8,8),
    (6,8),
    (4,4),
    (2,4),
    (1,4)
]


def quantize(x):

    best=4
    diff=999

    for value,q in GRID:
        d=abs(x-value)

        if d<diff:
            diff=d
            best=q

    return best



# -------------------------
# remove bad notation
# -------------------------

for tag in [
    "voice",
    "beam",
    "tie",
    "notations",
    "chord"
]:

    for e in root.findall(".//"+tag):
        parent=None

        for p in root.iter():
            if e in list(p):
                parent=p
                break

        if parent is not None:
            parent.remove(e)



print("quantizing notes")


# -------------------------
# quantize duration
# -------------------------

for note in root.findall(".//note"):

    dur=note.find("duration")

    if dur is None:
        continue


    try:
        old=int(dur.text)

    except:
        continue


    new=quantize(old)

    dur.text=str(new)



# -------------------------
# remove invalid rests
# -------------------------

for rest in root.findall(".//rest"):

    dur=rest.find("../duration")



# -------------------------
# rebuild measure timeline
# -------------------------

print("rebuild measures")


for measure in root.findall(".//measure"):

    current=0

    notes=list(measure.findall("note"))


    for note in notes:

        dur=note.find("duration")

        if dur is None:
            continue


        d=int(dur.text)


        if current+d>64:

            # shorten note
            d=64-current
            dur.text=str(d)


        current+=d



    # fill empty

    if current<64:

        rest=ET.Element("note")

        ET.SubElement(rest,"rest")

        ET.SubElement(
            rest,
            "duration"
        ).text=str(64-current)


        measure.append(rest)



# -------------------------
# final check
# -------------------------

print("FINAL CHECK")


safe=True


for i,m in enumerate(root.findall(".//measure")):

    total=0

    for n in m.findall("note"):

        d=n.find("duration")

        if d is not None:
            total+=int(d.text)


    print(
        "Measure",
        i+1,
        total/16
    )


    if total!=64:
        safe=False



if safe:
    print("ALL MEASURES SAFE")
else:
    print("WARNING")


tree.write(
    OUTPUT,
    encoding="utf-8",
    xml_declaration=True
)


print("FINAL WRITE")
print("DONE")
print(OUTPUT)