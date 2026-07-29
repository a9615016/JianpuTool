import sys
import xml.etree.ElementTree as ET
from fractions import Fraction


print("######## JIANPU PREPARE V8 ########")


def quantize_duration(value):

    """
    MusicXML duration -> quarter length
    """

    targets = [
        Fraction(0),
        Fraction(1,4),
        Fraction(1,2),
        Fraction(3,4),
        Fraction(1),
        Fraction(3,2),
        Fraction(2),
        Fraction(3),
        Fraction(4),
    ]

    v = Fraction(value).limit_denominator(96)

    return float(
        min(
            targets,
            key=lambda x: abs(x-v)
        )
    )


def get_measure_length(measure):

    total = 0

    for note in measure.findall(".//note"):

        dur = note.find("duration")

        if dur is not None:
            total += float(dur.text)

    return total


def remove_bad_notations(root):

    for elem in root.iter():

        # remove tie
        for child in list(elem):

            if child.tag.endswith("tie"):
                elem.remove(child)


        # remove beam
        for child in list(elem):

            if child.tag.endswith("beam"):
                elem.remove(child)


def rebuild_measure(measure):

    notes = measure.findall("./note")

    total = 0


    for note in notes:

        dur = note.find("duration")

        if dur is None:
            continue


        q = float(dur.text)

        q = quantize_duration(q)

        dur.text = str(q)

        total += q



    # ------------------------
    # force 4/4
    # ------------------------

    if total > 4:


        overflow = total - 4


        for note in reversed(notes):

            dur = note.find("duration")

            if dur is None:
                continue


            d = float(dur.text)


            if d >= overflow:

                new_d = d-overflow


                if new_d <= 0:

                    measure.remove(note)

                else:

                    dur.text=str(new_d)


                break


            else:

                measure.remove(note)

                overflow -= d



    elif total < 4:


        rest = ET.Element(
            "note"
        )


        ET.SubElement(
            rest,
            "rest"
        )


        dur = ET.SubElement(
            rest,
            "duration"
        )

        dur.text=str(
            round(4-total,3)
        )


        measure.append(rest)



def check_measure(root):

    print("FINAL CHECK")


    for i,m in enumerate(
        root.findall(".//measure"),
        1
    ):

        length=get_measure_length(m)


        print(
            "Measure",
            i,
            length
        )

        if abs(length-4)>0.01:

            print(
                "WARNING",
                i,
                length
            )


def main():

    if len(sys.argv)<2:

        print(
            "usage: python jianpu_prepare_v8.py input.xml output.xml"
        )

        return


    infile=sys.argv[1]


    outfile=(
        sys.argv[2]
        if len(sys.argv)>2
        else
        "clean.musicxml"
    )


    print("INPUT:",infile)


    tree=ET.parse(infile)

    root=tree.getroot()


    print("remove ties")
    print("remove beams")

    remove_bad_notations(root)



    print("duration quantize")

    for measure in root.findall(".//measure"):

        rebuild_measure(
            measure
        )



    print("rebuild measures")


    check_measure(root)



    tree.write(
        outfile,
        encoding="utf-8",
        xml_declaration=True
    )


    print("FINAL WRITE")
    print("DONE")
    print(outfile)



if __name__=="__main__":
    main()