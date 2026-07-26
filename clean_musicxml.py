import sys
import xml.etree.ElementTree as ET


print("CLEAN MUSICXML V3")


if len(sys.argv) < 3:
    print("使用:")
    print("python clean_musicxml_v3.py input.musicxml output.musicxml")
    sys.exit(1)


input_file = sys.argv[1]
output_file = sys.argv[2]


print("input:")
print(input_file)

print("output:")
print(output_file)


ET.register_namespace("", "http://www.musicxml.org/ns/musicxml")


tree = ET.parse(input_file)
root = tree.getroot()


ns = {
    "m": "http://www.musicxml.org/ns/musicxml"
}


print("讀取 MusicXML")


# ==========================
# 固定 divisions
# ==========================

for div in root.findall(".//m:divisions", ns):
    div.text = "16"


# ==========================
# 固定拍號 4/4
# ==========================

for measure_attr in root.findall(".//m:time", ns):

    beats = measure_attr.find("m:beats", ns)
    beat_type = measure_attr.find("m:beat-type", ns)

    if beats is not None:
        beats.text = "4"

    if beat_type is not None:
        beat_type.text = "4"


# ==========================
# 移除 tie
# ==========================

for tie in root.findall(".//m:tie", ns):
    parent = None

    for p in root.iter():
        if tie in list(p):
            parent = p
            break

    if parent is not None:
        parent.remove(tie)


for tied in root.findall(".//m:tied", ns):

    parent = None

    for p in root.iter():
        if tied in list(p):
            parent = p
            break

    if parent is not None:
        parent.remove(tied)



# ==========================
# 移除 grace note
# ==========================

for grace in root.findall(".//m:grace", ns):

    parent = None

    for p in root.iter():
        if grace in list(p):
            parent = p
            break

    if parent is not None:
        parent.remove(grace)



# ==========================
# 修正 duration
# ==========================

print("修正 duration")


for note in root.findall(".//m:note", ns):

    duration = note.find("m:duration", ns)

    if duration is not None:

        try:
            value = int(duration.text)

            # 最高限制
            if value > 64:
                duration.text = "16"

            # 太小
            if value <= 0:
                duration.text = "16"

        except:
            duration.text = "16"



# ==========================
# 移除 voice
# ==========================

for voice in root.findall(".//m:voice", ns):

    parent = None

    for p in root.iter():
        if voice in list(p):
            parent = p
            break

    if parent is not None:
        parent.remove(voice)



# ==========================
# 移除 chord
# ==========================

print("移除 chord")


for chord in root.findall(".//m:chord", ns):

    parent=None

    for p in root.iter():
        if chord in list(p):
            parent=p
            break

    if parent is not None:
        parent.remove(chord)



print("重新整理小節")


# ==========================
# measure reset
# ==========================

measures = root.findall(".//m:measure", ns)


for measure in measures:

    notes = measure.findall("m:note", ns)

    total = 0


    for note in notes:

        duration = note.find("m:duration", ns)

        if duration is not None:

            try:
                total += int(duration.text)

            except:
                pass



    # 4/4 = 64 ticks
    if total > 64:

        print(
            "trim measure:",
            measure.attrib.get("number"),
            total
        )


        current = 0


        for note in notes:

            duration = note.find("m:duration", ns)

            if duration is None:
                continue


            try:
                d=int(duration.text)

            except:
                d=16


            if current+d > 64:

                duration.text="16"

                current +=16

            else:

                current+=d



print("寫入檔案")


tree.write(
    output_file,
    encoding="utf-8",
    xml_declaration=True
)


print("完成:")
print(output_file)