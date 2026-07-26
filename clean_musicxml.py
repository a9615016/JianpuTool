import sys
import xml.etree.ElementTree as ET

print("CLEAN MUSICXML V6")


if len(sys.argv) < 3:
    print("python clean_musicxml.py input.musicxml output.musicxml")
    exit()


input_file = sys.argv[1]
output_file = sys.argv[2]


print("input:")
print(input_file)

print("output:")
print(output_file)


tree = ET.parse(input_file)
root = tree.getroot()


def tag(e):
    return e.tag.split("}")[-1]


def find(e, name):
    for x in e:
        if tag(x) == name:
            return x
    return None


print("讀取 MusicXML")


# -------------------------
# 強制 divisions = 16
# -------------------------

for div in root.iter():

    if tag(div) == "divisions":
        div.text = "16"


# -------------------------
# 處理 measures
# -------------------------

for measure in root.iter():

    if tag(measure) != "measure":
        continue


    print(
        "處理小節:",
        measure.attrib.get("number")
    )


    notes = []


    for child in list(measure):

        if tag(child) == "note":

            # 移除 chord
            for c in list(child):

                if tag(c) == "chord":
                    child.remove(c)


            # 移除 voice 2
            voice = find(child,"voice")

            if voice is not None:
                if voice.text != "1":
                    measure.remove(child)
                    continue


            notes.append(child)



    # ---------------------
    # 重新計算
    # ---------------------

    used = 0


    for note in notes:

        dur = find(note,"duration")

        if dur is None:
            continue


        value = int(dur.text)


        # 超過64直接截斷
        if used + value > 64:

            remain = 64-used

            if remain > 0:
                dur.text=str(remain)
                used=64

            else:
                measure.remove(note)

            continue


        used += value



    # ---------------------
    # 補 rest
    # ---------------------

    if used < 64:


        remain = 64-used


        print(
            "補休止:",
            remain
        )


        rest = ET.Element(
            "note"
        )


        ET.SubElement(
            rest,
            "rest"
        )


        duration = ET.SubElement(
            rest,
            "duration"
        )

        duration.text=str(remain)


        voice = ET.SubElement(
            rest,
            "voice"
        )

        voice.text="1"


        measure.append(rest)



# -------------------------
# 寫檔
# -------------------------

print("寫入")


tree.write(
    output_file,
    encoding="utf-8",
    xml_declaration=True
)


print("完成:")
print(output_file)