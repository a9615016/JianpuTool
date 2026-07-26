import sys
import xml.etree.ElementTree as ET
import copy


print("CLEAN MUSICXML V7")


if len(sys.argv) < 3:
    print("usage: python clean_musicxml_v7.py input.musicxml output.musicxml")
    sys.exit(1)


input_file = sys.argv[1]
output_file = sys.argv[2]


print("input:")
print(input_file)

print("output:")
print(output_file)


tree = ET.parse(input_file)
root = tree.getroot()


ns = ""
if root.tag.startswith("{"):
    ns = root.tag.split("}")[0] + "}"


def tag(name):
    return ns + name


# -------------------------
# divisions
# -------------------------

divisions = 16

for d in root.iter(tag("divisions")):
    d.text = str(divisions)


BAR_LENGTH = divisions * 4   # 4/4 = 64


print("BAR LENGTH:", BAR_LENGTH)



# -------------------------
# 清理 note
# -------------------------

for measure in root.iter(tag("measure")):

    notes = list(measure.findall(tag("note")))

    if not notes:
        continue


    current = 0
    new_notes = []


    for note in notes:

        duration_node = note.find(tag("duration"))

        if duration_node is None:
            continue


        try:
            duration = int(duration_node.text)

        except:
            duration = divisions


        # 移除 chord
        chord = note.find(tag("chord"))
        if chord is not None:
            note.remove(chord)



        # 防止超過小節
        remain = BAR_LENGTH - current


        if remain <= 0:
            break


        if duration > remain:
            duration = remain


        duration_node.text = str(duration)


        new_notes.append(note)


        current += duration



    # -------------------------
    # 補 rest
    # -------------------------

    if current < BAR_LENGTH:

        rest_duration = BAR_LENGTH - current


        rest = ET.Element(tag("note"))

        rest_tag = ET.SubElement(
            rest,
            tag("rest")
        )


        dur = ET.SubElement(
            rest,
            tag("duration")
        )

        dur.text = str(rest_duration)


        voice = ET.SubElement(
            rest,
            tag("voice")
        )

        voice.text = "1"


        new_notes.append(rest)


    # -------------------------
    # 重建 measure
    # -------------------------

    for n in notes:
        measure.remove(n)


    for n in new_notes:
        measure.append(n)



# -------------------------
# 移除多餘聲部
# -------------------------

for voice in root.iter(tag("voice")):
    voice.text = "1"



# -------------------------
# 移除 tie
# -------------------------

for tie in list(root.iter(tag("tie"))):
    parent = None


# -------------------------
# 寫出
# -------------------------

tree.write(
    output_file,
    encoding="utf-8",
    xml_declaration=True
)


print("完成:")
print(output_file)