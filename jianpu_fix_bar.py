from lxml import etree
import sys

if len(sys.argv) < 3:
    print("python jianpu_fix_bar.py input.musicxml output.musicxml")
    exit()

inp = sys.argv[1]
out = sys.argv[2]

tree = etree.parse(inp)
root = tree.getroot()

DIV = 16       # divisions
BAR = DIV * 4   # 4/4 = 64

print("JIANPU BAR FIX")

for measure in root.xpath(".//measure"):

    total = 0

    notes = list(measure.xpath("./note"))

    for n in notes:

        d = n.find("duration")

        if d is None:
            continue

        try:
            dur = int(d.text)
        except:
            continue

        total += dur

    # 超過小節就縮短最後音符
    if total > BAR:

        print(
            "FIX measure",
            measure.get("number"),
            total
        )

        overflow = total - BAR

        for n in reversed(notes):

            d = n.find("duration")

            if d is None:
                continue

            try:
                dur = int(d.text)
            except:
                continue

            if dur > overflow:

                d.text = str(dur-overflow)
                break


tree.write(
    out,
    encoding="utf-8",
    xml_declaration=True
)

print("DONE", out)