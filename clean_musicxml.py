import sys
import os
import xml.etree.ElementTree as ET
from fractions import Fraction


print("CLEAN VERSION 20260726 V7")


if len(sys.argv) < 2:
    print("usage: python clean_musicxml.py input.musicxml output.musicxml")
    sys.exit(1)


input_file = sys.argv[1]

if len(sys.argv) >= 3:
    output_file = sys.argv[2]
else:
    output_file = input_file.replace(
        ".musicxml",
        "_clean.musicxml"
    )


print("input:", input_file)


tree = ET.parse(input_file)
root = tree.getroot()


# MusicXML namespace
ns = {
    "m": "http://www.musicxml.org/ns/musicxml"
}


# =========================
# remove voices
# =========================

print("remove voices")

for voice in root.findall(".//m:voice", ns):
    parent = None
    for p in root.iter():
        if voice in list(p):
            parent = p
            break

    if parent is not None:
        parent.remove(voice)



# =========================
# remove chords
# =========================

print("remove chords")

for chord in root.findall(".//m:chord", ns):
    parent = None

    for p in root.iter():
        if chord in list(p):
            parent = p
            break

    if parent is not None:
        parent.remove(chord)



# =========================
# remove grace
# =========================

print("remove grace")

for grace in root.findall(".//m:grace", ns):
    parent = None

    for p in root.iter():
        if grace in list(p):
            parent = p
            break

    if parent is not None:
        parent.remove(grace)



# =========================
# fix note durations
# =========================

print("fix duration")


for note in root.findall(".//m:note", ns):

    duration = note.find("m:duration", ns)
    typ = note.find("m:type", ns)


    if typ is not None:

        value = typ.text


        # 禁止128分音符
        if value == "128th":
            print("convert 128th -> 64th")

            typ.text = "64th"

            if duration is not None:
                d = int(duration.text)
                duration.text = str(max(1, d * 2))


        # 64以上保持
        elif value == "256th":
            print("convert 256th -> 64th")

            typ.text = "64th"

            if duration is not None:
                d = int(duration.text)
                duration.text = str(max(1, d * 4))



# =========================
# remove tuplets
# =========================

print("remove tuplets")


for tuplet in root.findall(".//m:tuplet", ns):

    parent=None

    for p in root.iter():
        if tuplet in list(p):
            parent=p
            break

    if parent is not None:
        parent.remove(tuplet)



# =========================
# rebuild measure duration
# =========================

print("rebuild measures")


divisions = 16


for measure in root.findall(".//m:measure", ns):

    notes = measure.findall(
        ".//m:note",
        ns
    )


    total = 0

    for note in notes:

        duration = note.find(
            "m:duration",
            ns
        )

        if duration is not None:

            total += int(duration.text)



    # 4/4 = 64 ticks
    target = 64


    if total > target:

        print(
            "fix measure overflow",
            measure.attrib.get("number"),
            total
        )


        overflow = total - target


        for note in reversed(notes):

            duration = note.find(
                "m:duration",
                ns
            )

            if duration is None:
                continue


            d=int(duration.text)


            if d > overflow:

                duration.text=str(
                    d-overflow
                )

                break

            else:

                duration.text="1"

                overflow-=d




# =========================
# final cleanup
# =========================

print("final cleanup")


for elem in root.iter():

    if elem.text:

        elem.text=elem.text.strip()



# =========================
# write
# =========================

print("write")

tree.write(
    output_file,
    encoding="utf-8",
    xml_declaration=True
)


print(
    "done:",
    output_file
)