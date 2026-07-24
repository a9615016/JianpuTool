import sys
from lxml import etree


input_file=sys.argv[1]
output_file=sys.argv[2]


tree=etree.parse(input_file)

root=tree.getroot()


# 強制全部 time 4/4

for time in root.xpath(".//time"):

    beats=time.find("beats")
    beat_type=time.find("beat-type")

    if beats is not None:
        beats.text="4"

    if beat_type is not None:
        beat_type.text="4"



# 移除 pickup

for measure in root.xpath(".//measure"):

    attrs=measure.find("attributes")

    if attrs is not None:

        for st in attrs.findall("time"):

            attrs.remove(st)



tree.write(
    output_file,
    encoding="UTF-8",
    xml_declaration=True
)


print("fix完成")