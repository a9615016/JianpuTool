import sys
import os
import xml.etree.ElementTree as ET


print("CLEAN VERSION 20260726 V21.1")


if len(sys.argv) < 2:
    print("usage: python clean_musicxml.py input.musicxml [output.musicxml]")
    sys.exit(1)


input_file = sys.argv[1]

if len(sys.argv) >= 3:
    output_file = sys.argv[2]
else:
    base = os.path.splitext(input_file)[0]
    output_file = base + "_clean.musicxml"


print("input:", input_file)


tree = ET.parse(input_file)
root = tree.getroot()


# ==========================
# namespace
# ==========================

ns = {}

if root.tag.startswith("{"):
    ns["m"] = root.tag.split("}")[0].strip("{")


def tag(name):
    if ns:
        return "{%s}%s" % (ns["m"], name)
    return name


# ==========================
# remove voices
# ==========================

print("remove voices")

for elem in root.iter(tag("voice")):
    elem.text = "1"


# ==========================
# remove chords
# ==========================

print("remove chords")

for note in root.iter(tag("note")):
    for child in list(note):
        if child.tag.endswith("chord"):
            note.remove(child)


# ==========================
# remove grace
# ==========================

print("remove grace")

for note in root.iter(tag("note")):
    for child in list(note):
        if child.tag.endswith("grace"):
            note.remove(child)


# ==========================
# force 4/4
# ==========================

print("force 4/4")


for time in root.iter(tag("time")):

    beats = time.find(tag("beats"))
    beat_type = time.find(tag("beat-type"))

    if beats is not None:
        beats.text = "4"

    if beat_type is not None:
        beat_type.text = "4"


# ==========================
# V21 duration fix
# ==========================

print("fix durations V21")


valid = [
    0.5,
    0.75,
    1,
    1.5,
    2,
    3,
    4,
    6,
    8,
    12
]


for duration in root.iter(tag("duration")):

    try:

        value = float(duration.text)

        if value not in valid:

            print(
                "V21 fix duration:",
                value,
                "-> 4"
            )

            duration.text = "4"

    except:

        duration.text = "4"



# ==========================
# remove invalid time
# ==========================
# ==========================
# FINAL JIANPU FIX V21.1
# ==========================

print("fix measure duration V21.1")


for measure in root.iter(tag("measure")):

    total = 0

    for duration in measure.iter(tag("duration")):

        try:
            total += float(duration.text)

        except:
            pass


    # jianpu_ly 常用 4/4:
    # quarter = 4
    # measure = 16

    # 發現異常小節直接重置

    if total not in [
        4,
        8,
        12,
        16,
        32,
        48,
        64
    ]:

        print(
            "V21.1 fix measure:",
            total,
            "-> normalize"
        )


        durations = list(
            measure.iter(tag("duration"))
        )


        if len(durations) > 0:

            each = 16 / len(durations)


            for d in durations:

                d.text = str(each)



    print("V21.1 measure fix done")
    # ==========================
    # remove invalid time
    # ==========================

    print("remove invalid time")

    # V21.1 final pass
    for elem in root.iter():
    if elem.tag.endswith("measure-style"):
        continue



# ==========================
# FINAL WRITE
# ==========================


tree.write(
    output_file,
    encoding="utf-8",
    xml_declaration=True
)


print("V21 DONE:")
print(output_file)