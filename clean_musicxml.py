import sys
import xml.etree.ElementTree as ET
import copy

NS = "http://www.musicxml.org/ns/musicxml"
ET.register_namespace("", NS)

TARGET_DURATION = 64


def tag(name):
    return f"{{{NS}}}{name}"


def get_duration(note):
    d = note.find(tag("duration"))
    if d is not None:
        return int(d.text)
    return 0


def set_duration(note, value):
    d = note.find(tag("duration"))
    if d is not None:
        d.text = str(value)


def create_rest(duration):
    note = ET.Element(tag("note"))

    rest = ET.SubElement(note, tag("rest"))

    duration_node = ET.SubElement(
        note,
        tag("duration")
    )
    duration_node.text = str(duration)

    voice = ET.SubElement(
        note,
        tag("voice")
    )
    voice.text = "1"

    return note


def clean_measure(measure):

    notes = measure.findall(tag("note"))

    total = sum(get_duration(n) for n in notes)

    print(
        "measure duration before:",
        total
    )

    # 超過64
    if total > TARGET_DURATION:

        overflow = total - TARGET_DURATION

        print(
            "remove overflow:",
            overflow
        )

        for note in reversed(notes):

            if overflow <= 0:
                break

            # 只刪 rest
            rest = note.find(tag("rest"))

            if rest is not None:

                dur = get_duration(note)

                if dur <= overflow:
                    measure.remove(note)
                    overflow -= dur

                else:
                    set_duration(
                        note,
                        dur - overflow
                    )
                    overflow = 0


    # 重新計算
    notes = measure.findall(tag("note"))

    total = sum(
        get_duration(n)
        for n in notes
    )


    # 不足補休止
    if total < TARGET_DURATION:

        add = TARGET_DURATION - total

        print(
            "add rest:",
            add
        )

        measure.append(
            create_rest(add)
        )


    total = sum(
        get_duration(n)
        for n in measure.findall(tag("note"))
    )


    print(
        "measure duration after:",
        total
    )



def clean_musicxml(input_file, output_file):

    print("CLEAN MUSICXML FINAL V12")

    print("input:")
    print(input_file)

    print("output:")
    print(output_file)


    tree = ET.parse(input_file)
    root = tree.getroot()


    # divisions = 16

    for divisions in root.iter(tag("divisions")):
        divisions.text = "16"


    # 強制4/4

    for time in root.iter(tag("time")):

        beats = time.find(tag("beats"))
        beat_type = time.find(tag("beat-type"))

        if beats is not None:
            beats.text = "4"

        if beat_type is not None:
            beat_type.text = "4"



    for part in root.findall(tag("part")):

        for measure in part.findall(tag("measure")):


            # 移除 chord

            for chord in measure.findall(
                ".//" + tag("chord")
            ):
                parent = measure
                parent.remove(chord)



            # 保留 voice 1

            for note in list(
                measure.findall(tag("note"))
            ):

                voice = note.find(
                    tag("voice")
                )

                if voice is not None:
                    if voice.text != "1":
                        measure.remove(note)



            clean_measure(measure)



    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True
    )


    print("DONE")
    print(output_file)



if __name__ == "__main__":

    if len(sys.argv) < 3:

        print(
            "usage: python clean_musicxml_final_v12.py input.musicxml output.musicxml"
        )

        sys.exit(1)


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )