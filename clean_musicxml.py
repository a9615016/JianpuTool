import sys
import xml.etree.ElementTree as ET
import copy


print("CLEAN VERSION 20260726 V14")
print("force split measure crossing notes")


input_file = sys.argv[1]
output_file = sys.argv[2]


tree = ET.parse(input_file)
root = tree.getroot()


ns = {
    "m":"http://www.musicxml.org/ns/musicxml"
}


# divisions
divisions = None

for d in root.iter():
    if d.tag.endswith("divisions"):
        divisions = int(d.text)
        break


if divisions is None:
    divisions = 16


print("divisions:", divisions)



# 每小節容量
measure_length = divisions * 4

print("measure length:", measure_length)



for part in root.iter():

    if not part.tag.endswith("measure"):
        continue


    current = 0


    notes = list(part)


    for elem in notes:


        if not elem.tag.endswith("note"):
            continue


        duration_node = None

        for c in elem:

            if c.tag.endswith("duration"):
                duration_node=c
                break


        if duration_node is None:
            continue


        dur=int(duration_node.text)



        remain = measure_length-current



        # 超過小節
        if dur > remain:


            print(
                "split note:",
                dur,
                "remain:",
                remain
            )


            first = copy.deepcopy(elem)
            second = copy.deepcopy(elem)


            for x in first.iter():

                if x.tag.endswith("duration"):
                    x.text=str(remain)


            for x in second.iter():

                if x.tag.endswith("duration"):
                    x.text=str(dur-remain)



            # tie
            tie1=ET.SubElement(first,"tie")
            tie1.set("type","start")


            tie2=ET.SubElement(second,"tie")
            tie2.set("type","stop")



            index=list(part).index(elem)


            part.remove(elem)

            part.insert(index,first)

            part.insert(index+1,second)


            current=measure_length



        else:

            current += dur



    # 修正小節重新計算
    if current > measure_length:
        current=measure_length



tree.write(
    output_file,
    encoding="utf-8",
    xml_declaration=True
)


print("done:")
print(output_file)