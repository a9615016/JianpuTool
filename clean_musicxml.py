import sys
import copy
import xml.etree.ElementTree as ET


print("================")
print("CLEAN MUSICXML V66")
print("MEASURE SPLITTER ENGINE")
print("================")


INPUT = sys.argv[1]
OUTPUT = sys.argv[2] if len(sys.argv) > 2 else "clean.musicxml"


NS = "http://www.musicxml.org/ns/musicxml"

ET.register_namespace("", NS)


tree = ET.parse(INPUT)
root = tree.getroot()


def tag(name):
    return "{%s}%s" % (NS, name)



# -------------------------
# remove bad notation
# -------------------------

print("remove voices")
for e in root.findall(".//"+tag("voice")):
    e.text = None


print("remove chords")
for parent in root.iter():
    for child in list(parent):
        if child.tag == tag("chord"):
            parent.remove(child)


print("remove beams")
for e in root.findall(".//"+tag("beam")):
    for p in root.iter():
        if e in list(p):
            p.remove(e)


print("remove ties")
for e in root.findall(".//"+tag("tie")):
    for p in root.iter():
        if e in list(p):
            p.remove(e)



# -------------------------
# divisions = 16
# -------------------------

for attr in root.findall(".//"+tag("attributes")):

    div = attr.find(tag("divisions"))

    if div is not None:
        div.text="16"



# -------------------------
# copy note
# -------------------------

def clone_note(note, duration):

    n = copy.deepcopy(note)

    d = n.find(tag("duration"))

    if d is None:
        d = ET.SubElement(n, tag("duration"))

    d.text=str(duration)

    return n



# -------------------------
# split measure
# -------------------------

print("split cross measure notes")


for measure in root.findall(".//"+tag("measure")):

    notes = list(measure.findall(tag("note")))


    # remove originals
    for n in notes:
        measure.remove(n)


    cursor = 0


    for note in notes:

        dur_node = note.find(tag("duration"))

        if dur_node is None:
            continue


        try:
            duration=int(dur_node.text)

        except:
            continue



        remain = duration


        while remain > 0:


            available = 64 - cursor


            take = min(
                remain,
                available
            )


            new_note = clone_note(
                note,
                take
            )


            measure.append(new_note)


            cursor += take
            remain -= take



            if cursor >= 64:

                cursor = 0



    # fill rest

    if cursor > 0:

        rest = ET.Element(tag("note"))

        ET.SubElement(
            rest,
            tag("rest")
        )

        ET.SubElement(
            rest,
            tag("duration")
        ).text=str(64-cursor)


        measure.append(rest)



# -------------------------
# final check
# -------------------------

print("FINAL CHECK")


safe=True


for i,measure in enumerate(
        root.findall(".//"+tag("measure"))
    ):

    total=0

    for n in measure.findall(tag("note")):

        d=n.find(tag("duration"))

        if d is not None:
            total += int(d.text)


    beats=total/16

    print(
        "Measure",
        i+1,
        beats
    )


    if total != 64:
        safe=False



if safe:
    print("ALL MEASURES SAFE")
    print("ALL NOTES INSIDE BAR")
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