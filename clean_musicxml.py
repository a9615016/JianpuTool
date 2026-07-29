import sys
from lxml import etree


print("CLEAN VERSION 20260729 DEBUG")


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



def count_notes(root, label):

    count = len(
        root.xpath(".//note")
    )

    print(
        label,
        count
    )



def remove_chords(root):

    print("remove chords")

    for chord in root.xpath(".//chord"):

        parent = chord.getparent()

        if parent is not None:
            parent.remove(chord)



def remove_beams(root):

    print("remove beams")

    for beam in root.xpath(".//beam"):

        parent = beam.getparent()

        if parent is not None:
            parent.remove(beam)



def remove_ties(root):

    print("remove ties")

    for tie in root.xpath(".//tie"):

        parent = tie.getparent()

        if parent is not None:
            parent.remove(tie)



def force_44(root):

    print("force 4/4")

    for time in root.xpath(".//time"):

        beats=time.find("beats")
        beat=time.find("beat-type")

        if beats is not None:
            beats.text="4"

        if beat is not None:
            beat.text="4"



def get_divisions(root):

    div=root.find(".//divisions")

    if div is None:
        return 16

    return int(div.text)



def duration_quantize(root, divisions):

    print("duration quantize")

    for note in root.xpath(".//note"):

        duration=note.find("duration")

        if duration is None:
            continue


        old_tick=int(duration.text)

        old=old_tick/divisions


        new=closest_duration(old)


        if abs(old-new)>0.001:

            print(
                "duration fix:",
                old,
                "->",
                new
            )


            duration.text=str(
                int(new*divisions)
            )



def check_measures(root, divisions):

    print("FINAL CHECK")


    for measure in root.xpath(".//measure"):

        total=0


        for d in measure.xpath("./note/duration"):

            total+=int(d.text)


        beat=total/divisions


        print(
            "Measure",
            measure.get("number"),
            beat
        )


        if abs(beat-4)>0.1:

            print(
                "WARNING measure mismatch"
            )



def clean_musicxml(input_file, output_file):

    parser=etree.XMLParser(
        remove_blank_text=True
    )


    tree=etree.parse(
        input_file,
        parser
    )


    root=tree.getroot()


    # 原始音符數
    count_notes(
        root,
        "INPUT NOTES:"
    )


    divisions=get_divisions(root)


    remove_chords(root)

    remove_beams(root)

    remove_ties(root)


    # 清理後音符數
    count_notes(
        root,
        "AFTER CLEAN NOTES:"
    )


    force_44(root)


    duration_quantize(
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


    input_file=sys.argv[1]


    if len(sys.argv)>=3:

        output_file=sys.argv[2]

    else:

        output_file="clean.musicxml"



    clean_musicxml(
        input_file,
        output_file
    )