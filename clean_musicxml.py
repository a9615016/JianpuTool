from lxml import etree
import sys
import copy


print("CLEAN VERSION 20260729 V2")


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


def closest_duration(value):

    return min(
        VALID_DURATIONS,
        key=lambda x: abs(x-value)
    )



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



def duration_quantize(root, divisions):

    print("duration quantize")


    for note in root.xpath(".//note"):

        d=note.find("duration")

        if d is None:
            continue


        old=int(d.text)/divisions


        new=closest_duration(old)


        if abs(old-new)>0.001:

            print(
                "duration fix",
                old,
                "->",
                new
            )


            d.text=str(
                int(new*divisions)
            )



def split_cross_measure_notes(root, divisions):

    print("split cross measure notes")


    measures=root.xpath(".//measure")


    limit=divisions*4


    for measure in measures:


        total=0


        notes=measure.xpath("./note")


        for note in notes:


            d=note.find("duration")


            if d is None:
                continue


            dur=int(d.text)


            if total + dur > limit:


                remain = limit-total


                if remain > 0:

                    print(
                        "split note in measure",
                        measure.get("number"),
                        "duration",
                        dur
                    )


                    # 原音符縮短
                    d.text=str(remain)


                    # 建立下一段
                    new_note=copy.deepcopy(note)

                    new_d=new_note.find("duration")

                    new_d.text=str(
                        dur-remain
                    )


                    next_measure=None


                    index=measures.index(measure)


                    if index+1 < len(measures):
                        next_measure=measures[index+1]


                    if next_measure is not None:

                        next_measure.insert(
                            0,
                            new_note
                        )


                total=limit


            else:

                total+=dur



def check_measures(root, divisions):

    print("FINAL CHECK")


    for m in root.xpath(".//measure"):

        total=0


        for d in m.xpath("./note/duration"):

            total+=int(d.text)


        beat=total/divisions


        print(
            "Measure",
            m.get("number"),
            beat
        )


        if abs(beat-4)>0.01:

            print(
                "WARNING measure mismatch"
            )



def clean(input_file, output_file):


    parser=etree.XMLParser(
        remove_blank_text=True
    )


    tree=etree.parse(
        input_file,
        parser
    )


    root=tree.getroot()


    divisions=get_divisions(root)


    print(
        "NOTES:",
        len(root.xpath(".//note"))
    )


    remove_tags(root)


    force_44(root)


    duration_quantize(
        root,
        divisions
    )


    split_cross_measure_notes(
        root,
        divisions
    )


    check_measures(
        root,
        divisions
    )


    print("FINAL WRITE")


    tree.write(
        output_file,
        encoding="UTF-8",
        xml_declaration=True,
        pretty_print=True
    )


    print("DONE")
    print(output_file)



if __name__=="__main__":


    if len(sys.argv)<2:

        print(
            "python clean_musicxml.py input.musicxml [output.musicxml]"
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