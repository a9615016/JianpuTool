import sys
import xml.etree.ElementTree as ET
import copy


print("CLEAN MUSICXML FINAL V8")


def split_note(note, remain, duration):

    """
    切割跨小節音符

    例如:
    duration 16
    bar剩8

    變:
    第一小節 8
    下一小節 8
    """

    first = copy.deepcopy(note)
    second = copy.deepcopy(note)

    first.find("duration").text = str(remain)

    second.find("duration").text = str(duration - remain)

    return first, second



def clean_musicxml(input_file, output_file):

    print("input:")
    print(input_file)

    print("output:")
    print(output_file)


    tree = ET.parse(input_file)
    root = tree.getroot()


    namespace = ""

    for elem in root.iter():
        if "}" in elem.tag:
            namespace = elem.tag.split("}")[0] + "}"


    def tag(x):
        return namespace + x


    # divisions
    divisions = root.find(
        ".//" + tag("divisions")
    )

    if divisions is not None:
        divisions.text = "16"


    print("remove backup forward")
    

    # 移除 backup forward
    for measure in root.iter(tag("measure")):

        for child in list(measure):

            if child.tag in [
                tag("backup"),
                tag("forward")
            ]:
                measure.remove(child)



    print("remove chords")


    # 移除 chord 標記
    for note in root.iter(tag("note")):

        for c in list(note):

            if c.tag == tag("chord"):
                note.remove(c)



    print("keep voice 1")


    # 移除 voice 2+
    for measure in root.iter(tag("measure")):

        for note in list(
            measure.findall(tag("note"))
        ):

            voice = note.find(tag("voice"))

            if voice is not None:

                if voice.text != "1":
                    measure.remove(note)



    print("split crossing notes")


    # 4/4
    BAR_LENGTH = 64


    for measure in root.iter(tag("measure")):

        notes = list(
            measure.findall(tag("note"))
        )


        new_notes=[]

        current = 0


        for note in notes:

            dur = note.find(tag("duration"))

            if dur is None:
                continue


            value=int(dur.text)


            if current + value > BAR_LENGTH:


                remain = BAR_LENGTH-current


                if remain > 0:


                    a,b = split_note(
                        note,
                        remain,
                        value
                    )


                    new_notes.append(a)


                    # 剩餘塞下一小節
                    dur.text=str(value-remain)

                    new_notes.append(b)

                    current=0


                else:

                    new_notes.append(note)

                    current=value


            else:

                new_notes.append(note)

                current += value



        # 重建 note
        old=list(measure.findall(tag("note")))

        for n in old:
            measure.remove(n)


        for n in new_notes:
            measure.append(n)



    print("fix duration")


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

        sys.exit(1)


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )