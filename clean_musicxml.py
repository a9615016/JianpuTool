import sys
import xml.etree.ElementTree as ET
import copy

print("CLEAN MUSICXML V5")


if len(sys.argv) < 3:
    print("usage:")
    print("python clean_musicxml.py input.musicxml output.musicxml")
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


DIVISION = 16

MEASURE_LENGTH = 64   # 4/4


print("讀取 MusicXML")


# -------------------------
# 移除 namespace helper
# -------------------------

def tag(e):
    return e.tag.split("}")[-1]


# -------------------------
# 處理每個 measure
# -------------------------

for measure in root.iter():

    if tag(measure) != "measure":
        continue


    print(
        "processing measure",
        measure.attrib.get("number")
    )


    notes = []

    for child in list(measure):

        if tag(child) == "note":

            # 移除 chord
            for c in list(child):
                if tag(c) == "chord":
                    child.remove(c)


            notes.append(child)


    # ---------------------
    # 計算 duration
    # ---------------------

    total = 0

    for n in notes:

        d = n.find("{*}duration")

        if d is not None:
            try:
                total += int(d.text)
            except:
                pass


    print(
        "measure duration:",
        total
    )


    # ---------------------
    # 超過小節
    # 刪除最後超出的 note
    # ---------------------

    if total > MEASURE_LENGTH:

        print(
            "trim overflow",
            total
        )

        current = 0

        for n in list(notes):

            d = n.find("{*}duration")

            if d is None:
                continue

            value = int(d.text)


            if current + value > MEASURE_LENGTH:

                measure.remove(n)

            else:

                current += value



    # ---------------------
    # 不足補 rest
    # ---------------------

    total = 0

    for n in measure:

        if tag(n) == "note":

            d = n.find("{*}duration")

            if d is not None:

                total += int(d.text)


    if total < MEASURE_LENGTH:

        remain = MEASURE_LENGTH - total


        print(
            "add rest:",
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

        duration.text = str(remain)


        voice = ET.SubElement(
            rest,
            "voice"
        )

        voice.text="1"


        measure.append(rest)



# -------------------------
# 寫出
# -------------------------

print("寫入檔案")


tree.write(
    output_file,
    encoding="utf-8",
    xml_declaration=True
)


print("完成:")
print(output_file)
