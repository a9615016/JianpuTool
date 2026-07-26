import sys
import os
import xml.etree.ElementTree as ET


VERSION = "CLEAN VERSION 20260726 V11"


NS = {
    "m": "http://www.musicxml.org/ns/musicxml"
}

ET.register_namespace("", NS["m"])


def T(name):
    return f"{{{NS['m']}}}{name}"


def remove_tag(parent, name):
    for x in list(parent):
        if x.tag == T(name):
            parent.remove(x)


def make_rest(duration):

    note = ET.Element(T("note"))

    ET.SubElement(
        note,
        T("rest")
    )

    dur = ET.SubElement(
        note,
        T("duration")
    )

    dur.text = str(duration)

    return note



def clean_musicxml(inp, out):

    print(VERSION)
    print("input:", inp)


    tree = ET.parse(inp)
    root = tree.getroot()


    divisions = 16
    measure_length = 64


    # ------------------
    # 固定 divisions
    # ------------------

    for d in root.iter(T("divisions")):
        d.text = str(divisions)



    print("remove voices")

    for note in root.iter(T("note")):

        remove_tag(note,"voice")
        remove_tag(note,"chord")
        remove_tag(note,"grace")



    print("fix duration")


    for note in root.iter(T("note")):

        dur = note.find(T("duration"))

        if dur is not None:

            try:

                value = int(dur.text)

                # 避免太小碎音
                if value < 2:
                    value = 2

                dur.text = str(value)

            except:
                pass



    print("rebuild measures")



    for no, measure in enumerate(
        root.iter(T("measure")),
        1
    ):

        notes = measure.findall(
            T("note")
        )


        total = 0


        for n in notes:

            d = n.find(T("duration"))

            if d is not None:

                total += int(d.text)



        print(
            "measure",
            no,
            "before:",
            total
        )



        # --------------------
        # 超過小節修正
        # --------------------

        if total > measure_length:


            remain = measure_length


            for n in list(notes):

                d = n.find(T("duration"))

                if d is None:
                    continue


                value = int(d.text)


                if remain <= 0:

                    measure.remove(n)


                elif value <= remain:

                    remain -= value


                else:

                    # 切斷最後音符

                    d.text = str(remain)

                    remain = 0



            total = measure_length



        # --------------------
        # 不足補休止
        # --------------------

        if total < measure_length:

            rest = measure_length-total

            print(
                "add rest:",
                rest
            )

            measure.append(
                make_rest(rest)
            )



        print(
            "measure",
            no,
            "after:",
            measure_length
        )



    print("final cleanup")



    tree.write(
        out,
        encoding="utf-8",
        xml_declaration=True
    )


    print(
        "done:",
        out
    )




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

        out=os.path.splitext(inp)[0]+"_clean.musicxml"



    clean_musicxml(
        inp,
        out
    )