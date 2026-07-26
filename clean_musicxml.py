import sys
import os
import xml.etree.ElementTree as ET


VERSION = "CLEAN VERSION 20260726 V10"

NS = {
    "m": "http://www.musicxml.org/ns/musicxml"
}

ET.register_namespace("", NS["m"])


def T(name):
    return f"{{{NS['m']}}}{name}"


def remove_child(parent, name):
    for x in list(parent):
        if x.tag == T(name):
            parent.remove(x)


def quantize(d, divisions=16):

    allowed = [
        divisions * 4,   # whole
        divisions * 2,   # half
        divisions,       # quarter
        divisions // 2,  # eighth
        divisions // 4   # sixteenth
    ]

    return min(
        allowed,
        key=lambda x: abs(x-d)
    )


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


    # ----------------------
    # divisions 固定
    # ----------------------

    for d in root.iter(T("divisions")):
        d.text = str(divisions)



    print("remove voices")

    for note in root.iter(T("note")):

        remove_child(note,"voice")
        remove_child(note,"chord")
        remove_child(note,"grace")



    print("quantize duration")


    for note in root.iter(T("note")):

        dur = note.find(T("duration"))

        if dur is not None:

            try:

                value = int(dur.text)

                dur.text = str(
                    quantize(
                        value,
                        divisions
                    )
                )

            except:
                pass



    print("rebuild measures")


    target = divisions * 4 * 4


    for measure_no, measure in enumerate(
        root.iter(T("measure")),
        1
    ):

        notes = measure.findall(
            T("note")
        )


        total = 0


        for n in notes:

            dur = n.find(
                T("duration")
            )

            if dur is not None:

                try:
                    total += int(dur.text)
                except:
                    pass



        print(
            "measure",
            measure_no,
            total
        )



        # ------------------
        # 超過小節
        # ------------------

        if total > target:

            overflow = total-target

            print(
                "trim",
                overflow
            )


            for n in reversed(notes):

                dur = n.find(
                    T("duration")
                )

                if dur is None:
                    continue


                value=int(dur.text)


                if overflow >= value:

                    measure.remove(n)

                    overflow -= value


                else:

                    dur.text=str(
                        value-overflow
                    )

                    break



        # ------------------
        # 不足補 rest
        # ------------------

        elif total < target:

            remain = target-total

            print(
                "add rest",
                remain
            )

            measure.append(
                make_rest(remain)
            )



    print("final cleanup")


    # 清除空 duration

    for d in root.iter(T("duration")):

        if d.text is None:
            d.text="16"



    tree.write(
        out,
        encoding="utf-8",
        xml_declaration=True
    )


    print("done:",out)




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