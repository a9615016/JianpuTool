import sys
import xml.etree.ElementTree as ET
import copy


print("CLEAN MUSICXML V4")


if len(sys.argv) < 3:
    print("Usage:")
    print("python clean_musicxml_v4.py input.musicxml output.musicxml")
    sys.exit(1)


input_file = sys.argv[1]
output_file = sys.argv[2]


print("input:")
print(input_file)

print("output:")
print(output_file)


tree = ET.parse(input_file)
root = tree.getroot()


ns = {
    "m": "http://www.musicxml.org/ns/musicxml"
}


# 處理 namespace
for elem in root.iter():
    if elem.tag.startswith("{"):
        elem.tag = elem.tag.split("}",1)[1]


print("讀取 MusicXML")


# divisions
divisions = 16


for d in root.iter("divisions"):
    divisions = int(d.text)
    break


print("divisions:", divisions)



# 找第一個 part
part = root.find(".//part")

if part is None:
    print("No part")
    sys.exit(1)



print("開始整理 notes")


notes = []


for measure in part.findall("measure"):

    for child in list(measure):

        if child.tag == "note":

            # 移除 chord
            chord = child.find("chord")
            if chord is not None:
                continue


            duration = child.find("duration")

            if duration is None:
                continue


            try:
                dur = int(duration.text)
            except:
                continue


            # 移除太短或異常
            if dur <= 0:
                continue


            notes.append(copy.deepcopy(child))



print("notes:", len(notes))



print("重新建立小節")


# 清空原 measures

for m in part.findall("measure"):
    part.remove(m)



measure_no = 1

current = 0


measure = ET.Element(
    "measure",
    {"number":str(measure_no)}
)


def add_measure():

    global measure_no, measure

    part.append(measure)

    measure_no += 1

    measure = ET.Element(
        "measure",
        {"number":str(measure_no)}
    )



for note in notes:


    duration_node = note.find("duration")

    dur = int(duration_node.text)



    # 超過小節拆開
    while dur > 0:


        remain = 64 - current


        if dur <= remain:


            new_note = copy.deepcopy(note)

            new_note.find("duration").text = str(dur)

            measure.append(new_note)

            current += dur

            dur = 0



        else:


            # 前半段

            part_note = copy.deepcopy(note)

            part_note.find("duration").text = str(remain)

            measure.append(part_note)


            dur -= remain


            current = 64



        if current >= 64:


            add_measure()

            current = 0



# 最後一小節

if len(measure):

    # 補休止符

    remain = 64-current

    if remain > 0:


        rest = ET.Element("note")


        ET.SubElement(rest,"rest")


        ET.SubElement(
            rest,
            "duration"
        ).text=str(remain)


        measure.append(rest)



    add_measure()



print("寫入檔案")


tree.write(
    output_file,
    encoding="utf-8",
    xml_declaration=True
)


print("完成:")
print(output_file)