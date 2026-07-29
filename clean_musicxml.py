from lxml import etree
import sys
import copy


print("CLEAN VERSION 20260729 V4 STRICT REBUILD")


def get_divisions(root):

    div = root.find(".//divisions")

    if div is None:
        return 16

    return int(div.text)



def remove_problem_tags(root):

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



def force_time(root):

    print("force 4/4")

    for t in root.xpath(".//time"):

        beats=t.find("beats")
        beat_type=t.find("beat-type")

        if beats is not None:
            beats.text="4"

        if beat_type is not None:
            beat_type.text="4"



def rebuild_part(part, divisions):

    print(
        "REBUILD PART",
        part.get("id")
    )


    measure_limit = divisions * 4


    old_measures = list(
        part.findall("measure")
    )


    if len(old_measures)==0:
        return


    # 保留第一個 measure 的 attributes

    first_attributes = old_measures[0].find(
        "attributes"
    )


    notes=[]


    for m in old_measures:

        for child in m:

            if child.tag=="note":

                notes.append(
                    copy.deepcopy(child)
                )



    print(
        "TOTAL NOTES:",
        len(notes)
    )


    # 移除舊 measures

    for m in old_measures:

        part.remove(m)



    new_measure_no=1

    current_measure=[]

    current_ticks=0



    for note in notes:


        duration=note.find("duration")


        if duration is None:

            continue


        ticks=int(duration.text)


        while current_ticks + ticks > measure_limit:


            remain = measure_limit-current_ticks


            if remain > 0:

                part_note=copy.deepcopy(note)

                part_note.find(
                    "duration"
                ).text=str(remain)


                current_measure.append(
                    part_note
                )


                print(
                    "split",
                    remain,
                    ticks-remain
                )


                ticks -= remain



            new_measure=etree.Element(
                "measure",
                number=str(new_measure_no)
            )


            if new_measure_no==1 and first_attributes is not None:

                new_measure.append(
                    copy.deepcopy(first_attributes)
                )


            for n in current_measure:

                new_measure.append(n)


            part.append(new_measure)


            new_measure_no+=1


            current_measure=[]

            current_ticks=0



            note=copy.deepcopy(note)

            note.find(
                "duration"
            ).text=str(ticks)



        current_measure.append(
            note
        )


        current_ticks += ticks



        if current_ticks == measure_limit:


            new_measure=etree.Element(
                "measure",
                number=str(new_measure_no)
            )


            if new_measure_no==1 and first_attributes is not None:

                new_measure.append(
                    copy.deepcopy(first_attributes)
                )


            for n in current_measure:

                new_measure.append(n)


            part.append(
                new_measure
            )


            new_measure_no+=1

            current_measure=[]

            current_ticks=0



    # 最後不足的小節

    if current_measure:


        new_measure=etree.Element(
            "measure",
            number=str(new_measure_no)
        )


        for n in current_measure:

            new_measure.append(n)


        part.append(new_measure)



def strict_check(root, divisions):

    print("STRICT CHECK")


    for m in root.xpath(".//measure"):

        ticks=0


        for d in m.xpath("./note/duration"):

            ticks += int(d.text)


        print(
            "Measure",
            m.get("number"),
            "ticks=",
            ticks,
            "beats=",
            ticks/divisions
        )


        if ticks > divisions*4:

            print(
                "ERROR OVER BAR"
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
        "INPUT NOTES",
        len(root.xpath(".//note"))
    )


    remove_problem_tags(root)


    force_time(root)


    for part in root.findall("part"):

        rebuild_part(
            part,
            divisions
        )


    strict_check(
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