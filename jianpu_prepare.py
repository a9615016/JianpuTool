import sys
import xml.etree.ElementTree as ET


print("================")
print("JIANPU PREPARE V1")
print("================")


src=sys.argv[1]
dst=sys.argv[2]


tree=ET.parse(src)

root=tree.getroot()


for elem in root.iter():

    if "}" in elem.tag:
        elem.tag=elem.tag.split("}",1)[1]



print("remove unsupported notation")


remove_tags=[
    "notations",
    "articulations",
    "ornaments",
    "technical",
    "dynamics"
]


for tag in remove_tags:

    for x in root.findall(".//"+tag):

        parent=None



print("force note duration")



for duration in root.findall(".//duration"):

    try:

        value=int(duration.text)

        if value < 1:
            duration.text="1"

    except:
        pass



print("remove empty measures")


for measure in root.findall(".//measure"):

    notes=measure.findall("note")

    if len(notes)==0:

        rest=ET.SubElement(measure,"note")

        ET.SubElement(rest,"rest")

        d=ET.SubElement(rest,"duration")

        d.text="64"



tree.write(
    dst,
    encoding="utf-8",
    xml_declaration=True
)


print("PREPARE DONE")
print(dst)