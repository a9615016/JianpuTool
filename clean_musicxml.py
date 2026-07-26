import xml.etree.ElementTree as ET
import sys
import os


INPUT = sys.argv[1]
OUTPUT = sys.argv[2] if len(sys.argv) > 2 else INPUT.replace(
    ".musicxml",
    "_clean.musicxml"
)


print("CLEAN VERSION 20260726 V13")
print("input:", INPUT)


tree = ET.parse(INPUT)
root = tree.getroot()


ns = {
    "m": "http://www.musicxml.org/ns/musicxml"
}


# remove voices
print("remove voices")

for note in root.findall(".//note"):
    voice = note.find("voice")
    if voice is not None:
        note.remove(voice)


# remove chords
print("remove chords")

for note in root.findall(".//note"):
    for c in note.findall("chord"):
        note.remove(c)


# remove grace
print("remove grace")

for note in root.findall(".//note"):
    for g in note.findall("grace"):
        note.remove(g)



print("quantize duration")


# divisions
divisions = root.find(".//divisions")

if divisions is None:
    div = 16
else:
    div = int(divisions.text)


TARGET = 64


print("repair measures")


measures = root.findall(".//measure")


for measure in measures:

    notes = measure.findall("note")

    total = 0


    for note in list(notes):

        duration = note.find("duration")

        if duration is None:
            continue


        d = int(duration.text)


        # quarter grid
        q = round(d / 4) * 4

        if q <= 0:
            q = 4


        duration.text = str(q)


        total += q



    # 修正超長小節

    if total > TARGET:

        overflow = total - TARGET

        print(
            "overflow measure",
            measure.attrib.get("number"),
            total
        )


        notes = measure.findall("note")


        while total > TARGET and notes:

            n = notes[-1]

            d = n.find("duration")

            if d is not None:

                old = int(d.text)

                remove = min(
                    old,
                    total - TARGET
                )

                new = old - remove

                if new <= 0:
                    measure.remove(n)
                else:
                    d.text = str(new)


                total -= remove

            notes.pop()



    # 不足補 rest

    if total < TARGET:

        rest = ET.Element("note")

        ET.SubElement(rest,"rest")

        dur = ET.SubElement(
            rest,
            "duration"
        )

        dur.text=str(
            TARGET-total
        )

        measure.append(rest)



print("final cleanup")


tree.write(
    OUTPUT,
    encoding="utf-8",
    xml_declaration=True
)


print("done:", OUTPUT)