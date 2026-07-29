from lxml import etree
import sys
import copy


print("CLEAN VERSION 20260729 V5 FLATTEN")


BAR_BEATS = 4


def get_divisions(root):

    div = root.find(".//divisions")

    if div is None:
        return 16

    return int(div.text)



def remove_time_tags(root):

    print("remove backup forward")

    for tag in ["backup", "forward"]:

        for x in root.xpath(f".//{tag}"):

            p=x.getparent()

            if p is not None:
                p.remove(x)



def remove_problem_tags(root):

    print("remove chord beam tie")

    for tag in [
        "chord",
        "beam",
        "tie"
    ]:

        for x in root.xpath(f".//{tag}"):

            p=x.getparent()

            if p is not None:
                p.remove(x)



def force_voice(root):

    print("force voice 1")

    for note in root.xpath(".//note"):

        voice=note.find("voice")

        if voice is None:

            voice=etree.Element("voice")

            note.append(voice)


        voice.text="1"



def force_time(root):

    print("force 4/4")

    for t in root.xpath(".//time"):

        b=t.find("beats")
        bt=t.find("beat-type")

        if b is not None:
            b.text="4"

        if bt is not None:
            bt.text="4"



def rebuild_measures(part, divisions):

    print("rebuild measures")


    limit=divisions*BAR_BEATS


    old=list(
        part.findall("measure")
    )


    notes=[]


    attributes=None


    for m in old:

        if attributes is None:

            a=m.find("attributes")

            if a is not None:

                attributes=copy.deepcopy(a)



        for n in m.findall("note"):

            notes.append(
                copy.deepcopy(n)
            )



    print(
        "NOTES",
        len(notes)
    )


    for m in old:

        part.remove(m)



    measure_no=1

    current=[]

    current_tick=0



    for note in notes:


        d=note.find("duration")


        if d is None:
            continue


        tick=int(d.text)



        while current_tick + tick > limit:


            remain=limit-current_tick


            if remain>0:

                n=copy.deepcopy(note)

                n.find(
                    "duration"
                ).text=str(remain)


                current.append(n)


                tick-=remain



            m=etree.Element(
                "measure",
                number=str(measure_no)
            )


            if measure_no==1 and attributes is not None:

                m.append(
                    copy.deepcopy(attributes)
                )


            for n in current:

                m.append(n)


            part.append(m)


            measure_no+=1

            current=[]

            current_tick=0



            note=copy.deepcopy(note)

            note.find(
                "duration"
            ).text=str(tick)



        current.append(note)

        current_tick+=tick



        if current_tick==limit:


            m=etree.Element(
                "measure",
                number=str(measure_no)
            )


            if measure_no==1 and attributes is not None:

                m.append(
                    copy.deepcopy(attributes)
                )


            for n in current:

                m.append(n)


            part.append(m)


            measure_no+=1

            current=[]

            current_tick=0



    if current:


        m=etree.Element(
            "measure",
            number=str(measure_no)
        )


        for n in current:

            m.append(n)


        part.append(m)



def check(root, divisions):

    print("FINAL CHECK")


    for m in root.xpath(".//measure"):

        total=0


        for d in m.xpath("./note/duration"):

            total+=int(d.text)


        print(
            "Measure",
            m.get("number"),
            "ticks",
            total
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


    remove_time_tags(root)

    remove_problem_tags(root)

    force_voice(root)

    force_time(root)



    for part in root.findall("part"):

        rebuild_measures(
            part,
            divisions
        )



    check(
        root,
        divisions
    )


    print("WRITE")


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