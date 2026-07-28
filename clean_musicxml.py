import sys
import xml.etree.ElementTree as ET
from fractions import Fraction

print("==============================")
print("CLEAN MUSICXML V70")
print("ABSOLUTE QUANTIZE ENGINE")
print("==============================")


STEP = 4       # 16th note tick
BAR = 64       # 4/4 with divisions=16


def q(v):
    return int(round(v / STEP) * STEP)


def duration_to_tick(note):
    dur = note.find("duration")
    if dur is None:
        return STEP
    return int(dur.text)


def make_rest(duration):
    note = ET.Element("note")

    ET.SubElement(note, "rest")

    d = ET.SubElement(note, "duration")
    d.text = str(duration)

    return note


def process(input_file, output_file):

    tree = ET.parse(input_file)
    root = tree.getroot()

    divisions = root.find(".//divisions")

    if divisions is not None:
        divisions.text = "16"


    print("remove voices")

    for v in root.findall(".//voice"):
        parent = v.getparent() if hasattr(v,"getparent") else None


    print("ABSOLUTE TIMELINE")


    for part in root.findall(".//part"):

        measures = list(part.findall("measure"))

        notes=[]

        absolute=0


        # collect notes
        for m in measures:

            for n in m.findall("note"):

                dur=n.find("duration")

                if dur is None:
                    continue

                d=int(dur.text)

                notes.append(
                    {
                    "note":n,
                    "start":absolute,
                    "dur":d
                    }
                )

                absolute+=d



        print(
            "notes:",
            len(notes),
            "ticks:",
            absolute
        )


        # quantize

        for item in notes:

            old=item["start"]

            new=q(old)

            diff=new-old

            item["start"]=new

            item["dur"]=max(
                STEP,
                q(item["dur"])
            )



        print("rebuild measures")


        # remove old measures

        for m in measures:
            part.remove(m)


        max_time=0

        for n in notes:
            max_time=max(
                max_time,
                n["start"]+n["dur"]
            )


        measure_count=max(
            1,
            (max_time+BAR-1)//BAR
        )


        print(
            "new measures:",
            measure_count
        )


        # create empty measures

        measure_notes=[[] for _ in range(measure_count)]


        for item in notes:

            index=item["start"]//BAR

            if index >= measure_count:
                index=measure_count-1

            measure_notes[index].append(item)



        # write measures

        for i,items in enumerate(measure_notes):

            m=ET.Element(
                "measure",
                {
                    "number":str(i+1)
                }
            )


            used=0


            for item in sorted(
                items,
                key=lambda x:x["start"]
            ):

                local=item["start"]%BAR

                gap=local-used

                if gap>0:
                    r=make_rest(gap)
                    m.append(r)
                    used+=gap


                n=item["note"]

                dur=n.find("duration")

                if dur is not None:
                    dur.text=str(
                        min(
                            item["dur"],
                            BAR-local
                        )
                    )

                m.append(n)

                used+=item["dur"]



            remain=BAR-used

            if remain>0:
                m.append(make_rest(remain))


            part.append(m)



    print("FINAL CHECK")


    for m in root.findall(".//measure"):

        total=0

        for n in m.findall("note"):

            d=n.find("duration")

            if d is not None:
                total+=int(d.text)


        print(
            "Measure",
            m.attrib.get("number"),
            total
        )


    print("FINAL WRITE")

    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True
    )


    print("DONE")
    print(output_file)



if __name__=="__main__":

    if len(sys.argv)<3:
        print(
        "usage: python clean_musicxml.py input.musicxml output.musicxml"
        )
        sys.exit()


    process(
        sys.argv[1],
        sys.argv[2]
    )