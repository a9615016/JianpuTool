import sys
import xml.etree.ElementTree as ET
from fractions import Fraction


print("================")
print("CLEAN MUSICXML V26 FINAL JIANPU COMPATIBLE")
print("================")


input_file = sys.argv[1]
output_file = sys.argv[2]


tree = ET.parse(input_file)
root = tree.getroot()


ns = {
    "m": "http://www.musicxml.org/ns/musicxml"
}


# 移除 namespace
for elem in root.iter():
    if "}" in elem.tag:
        elem.tag = elem.tag.split("}",1)[1]


print("remove voices")

for voice in root.findall(".//voice"):
    voice.text = None
    parent = None


print("remove chords")

for chord in root.findall(".//chord"):
    parent = None


print("remove beams")

for beam in root.findall(".//beam"):
    beam.text = None


print("remove ties")

for tie in root.findall(".//tie"):
    tie.text = None



print("force 4/4")

for time in root.findall(".//time"):
    for child in list(time):
        time.remove(child)

    beats = ET.SubElement(time,"beats")
    beats.text="4"

    beat_type = ET.SubElement(time,"beat-type")
    beat_type.text="4"



print("duration quantize")


# divisions
divisions = 16

for div in root.findall(".//divisions"):
    div.text=str(divisions)



allowed = [
    16,
    8,
    4,
    2,
    1
]


for duration in root.findall(".//duration"):

    try:
        value=int(duration.text)

        closest=min(
            allowed,
            key=lambda x:abs(x-value)
        )

        duration.text=str(closest)

    except:
        pass



print("remove invalid rests")

for measure in root.findall(".//measure"):

    notes=list(measure.findall("note"))

    total=0

    for note in notes:

        dur=note.find("duration")

        if dur is not None:
            try:
                total+=int(dur.text)
            except:
                pass


    # 超過小節直接刪最後音符
    while total>64 and notes:

        note=notes.pop()

        dur=note.find("duration")

        if dur is not None:
            total-=int(dur.text)

        measure.remove(note)



print("rebuild measures")

# 補 rest 到 64

for measure in root.findall(".//measure"):

    total=0

    for dur in measure.findall(".//duration"):

        try:
            total+=int(dur.text)
        except:
            pass


    if total < 64:

        rest=ET.Element("note")

        ET.SubElement(rest,"rest")

        d=ET.SubElement(rest,"duration")

        d.text=str(64-total)

        measure.append(rest)



print("FINAL CHECK")


ok=True

for i,m in enumerate(root.findall(".//measure"),1):

    total=0

    for d in m.findall(".//duration"):

        try:
            total+=int(d.text)
        except:
            pass


    beat=total/16

    print(
        "Measure",
        i,
        beat
    )

    if beat!=4:
        ok=False


if ok:
    print("ALL MEASURES SAFE")
else:
    print("WARNING")


print("FINAL WRITE")

tree.write(
    output_file,
    encoding="utf-8",
    xml_declaration=True
)


print("DONE")
print(output_file)