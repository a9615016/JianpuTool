import sys
import xml.etree.ElementTree as ET

NS = {
    "m": "http://www.musicxml.org/ns/musicxml"
}

ET.register_namespace("", NS["m"])


def tag(x):
    return f"{{{NS['m']}}}{x}"


file = sys.argv[1]

tree = ET.parse(file)
root = tree.getroot()


divisions = 16

for d in root.iter(tag("divisions")):
    divisions = int(d.text)
    break


print("divisions:", divisions)

target = divisions * 4 * 4

print("measure target:", target)


for i, measure in enumerate(
    root.iter(tag("measure")),
    1
):

    total = 0
    notes = 0


    for n in measure.findall(tag("note")):

        dur = n.find(tag("duration"))

        if dur is not None:
            total += int(dur.text)

        notes += 1


    print(
        "Measure",
        i,
        "notes:",
        notes,
        "duration:",
        total,
        "OK" if total == target else "ERROR"
    )