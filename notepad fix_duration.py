from lxml import etree
import sys

src = sys.argv[1]
dst = sys.argv[2]

tree = etree.parse(src)

count = 0

for elem in tree.xpath("//duration"):
    value = elem.text.strip()
    if "." in value:
        elem.text = str(int(float(value)))
        count += 1

tree.write(
    dst,
    encoding="UTF-8",
    xml_declaration=True
)

print("Fixed duration:", count)
print("Saved:", dst)