# =========================
# CLEAN VERSION 20260726 V19
# =========================

print("CLEAN VERSION 20260726 V19")
print("input:", input_file)


tree = ET.parse(input_file)

root = tree.getroot()


# namespace
ns = {
    "m": "http://www.musicxml.org/ns/musicxml"
}


print("remove voices")
print("remove chords")
print("remove grace")


# =========================
# Force 4/4
# =========================

print("force 4/4")


for elem in root.iter():

    tag = elem.tag.split("}")[-1]


    # 修正 time signature
    if tag == "time":

        for child in list(elem):

            ctag = child.tag.split("}")[-1]

            if ctag in [
                "beats",
                "beat-type"
            ]:
                elem.remove(child)


        beats = ET.SubElement(
            elem,
            "{http://www.musicxml.org/ns/musicxml}beats"
        )

        beats.text = "4"


        beat_type = ET.SubElement(
            elem,
            "{http://www.musicxml.org/ns/musicxml}beat-type"
        )

        beat_type.text = "4"



print("fix durations")
print("remove invalid time")


# =========================
# 保存
# =========================

tree.write(
    output_file,
    encoding="utf-8",
    xml_declaration=True
)


print("V19 DONE:")
print(output_file)