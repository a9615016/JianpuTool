from lxml import etree
import sys
import copy


print("CLEAN VERSION 20260729 V3 REBUILD")


BAR_BEATS = 4


VALID_DURATIONS = [
    0.5,
    0.75,
    1,
    1.5,
    2,
    3,
    4,
    6,
    8,
    12
]


def get_divisions(root):

    div = root.find(".//divisions")

    if div is None:
        return 16

    return int(div.text)



def remove_tags(root):

    print("remove chords")

    for x in root.xpath(".//chord"):
        p=x.getparent()
        if p is not None:
            p.remove(x)



    print("remove beams")

    for x in root.xpath(".//beam"):
        p=x.getparent()
        if p is not None:
            p.remove(x)



    print("remove ties")

    for x in root.xpath(".//tie"):
        p=x.getparent()
        if p is not None:
            p.remove(x)



def force_44(root):

    print("force 4/4")

    for t in root.xpath(".//time"):

        b=t.find("beats")
        bt=t.find("beat-type")

        if b is not None:
            b.text="4"

        if bt is not None:
            bt.text="4"



def quantize_duration(root, divisions):

    print("duration quantize")


    for d in root.xpath(".//duration"):

        value=int(d.text)


        # 四捨五入到最近 tick

        if value <= 0:
            value = divisions // 2


        d.text=str(value)



def rebuild_measures(root, divisions):

    print("REBUILD MEASURES")


    limit = divisions * BAR_BEATS


    part=root.find(".//part")


    if part is None:
        return


    old_measures=list(
        part.findall("measure")
    )


    all_notes=[]


    for m in old_measures:

        for n in m.findall("note"):

            all_notes.append(
                copy.deepcopy(n)
            )



    print(
        "TOTAL NOTES",
        len(all_notes)
    )


    # 清空舊小節

    for m in old_measures:

        part.remove(m)



    measure_no=1

    current=[]

    current_time=0



    for note in all_notes:


        d=note.find("duration")


        if d is None:

            continue


        dur=int(d.text)



        # 音符超過小節

        while current_time + dur > limit:


            remain = limit-current_time


            if remain > 0:

                first=copy.deepcopy(note)

                first.find("duration").text=str(remain)


                current.append(first)


                dur -= remain


                print(
                    "split note",
                    remain,
                    dur
                )



            new_measure=etree.Element(
                "measure",
                number=str(measure_no)
            )


            for n in current:

                new_measure.append(n)



            part.append(
                new_measure
            )


            measure_no+=1


            current=[]

            current_time=0



            note=copy.deepcopy(note)

            note.find("duration").text=str(dur)



        current.append(note)

        current_time += dur



        if current_time == limit:


            new_measure=etree.Element(
                "measure",
                number=str(measure_no)
            )


            for n in current:

                new_measure.append(n)


            part.append(
                new_measure
            )


            measure_no+=1

            current=[]

            current_time=0



    # 最後小節

    if current:


        new_measure=etree.Element(
            "measure",
            number=str(measure_no)
        )


        for n in current:

            new_measure.append(n)


        part.append(
            new_measure
        )



def check(root, divisions):

    print("FINAL CHECK")


    for m in root.xpath(".//measure"):

        total=0


        for d in m.xpath("./note/duration"):

            total+=int(d.text)



        print(
            "Measure",
            m.get("number"),
            total/divisions
        )



def clean(inp,out):


    parser=etree.XMLParser(
        remove_blank_text=True
    )


    tree=etree.parse(
        inp,
        parser
    )


    root=tree.getroot()


    divisions=get_divisions(root)


    print(
        "INPUT NOTES:",
        len(root.xpath(".//note"))
    )


    remove_tags(root)

    force_44(root)

    quantize_duration(
        root,
        divisions
    )


    rebuild_measures(
        root,
        divisions
    )


    check(
        root,
        divisions
    )



    print("FINAL WRITE")


    tree.write(
        out,
        encoding="UTF-8",
        xml_declaration=True,
        pretty_print=True
    )


    print("DONE")
    print(out)



if __name__=="__main__":


    if len(sys.argv)<2:

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        exit()



    inp=sys.argv[1]


    if len(sys.argv)>=3:
        out=sys.argv[2]
    else:
        out="clean.musicxml"



    clean(
        inp,
        out
    )