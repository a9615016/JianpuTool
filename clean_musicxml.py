import xml.etree.ElementTree as ET
import sys
import copy

NS = {
    "": "http://www.musicxml.org/ns/musicxml"
}

ET.register_namespace("", NS[""])


TARGET = 64   # 4/4 * divisions16


def tag(x):
    return x.split("}")[-1]


def make_rest(duration):
    note = ET.Element("note")

    ET.SubElement(note, "rest")

    d = ET.SubElement(note, "duration")
    d.text = str(duration)

    ET.SubElement(note, "voice").text = "1"

    return note


def clean(input_file, output_file):

    tree = ET.parse(input_file)
    root = tree.getroot()


    # divisions
    for d in root.iter():
        if tag(d.tag) == "divisions":
            d.text = "16"


    for measure in root.iter():

        if tag(measure.tag) != "measure":
            continue


        notes = []

        for n in list(measure):

            if tag(n.tag) != "note":
                continue


            # remove chord
            for c in list(n):
                if tag(c.tag) == "chord":
                    n.remove(c)


            # keep voice 1
            voice = n.find("voice")

            if voice is not None:
                if voice.text != "1":
                    measure.remove(n)
                    continue


            notes.append(n)



        # calculate duration

        total = 0

        for n in notes:

            dur = n.find("duration")

            if dur is not None:
                total += int(dur.text)



        # too long
        while total > TARGET:

            last = notes[-1]

            dur = last.find("duration")

            if dur is None:
                break


            value = int(dur.text)

            reduce = total - TARGET


            if value > reduce:

                dur.text = str(value-reduce)
                total = TARGET

            else:

                measure.remove(last)

                notes.pop()

                total -= value



        # too short

        if total < TARGET:

            rest = make_rest(
                TARGET-total
            )

            measure.append(rest)



    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True
    )


    print("CLEAN MUSICXML FINAL V11")
    print("DONE")
    print(output_file)



if __name__ == "__main__":

    clean(
        sys.argv[1],
        sys.argv[2]
    )