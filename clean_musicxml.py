import xml.etree.ElementTree as ET
import sys

REMOVE_TAGS = {
    "direction",
    "direction-type",
    "dynamics",
    "wedge",
    "metronome",
    "sound",
    "lyric",
    "notations",
    "articulations",
    "ornaments",
    "technical",
    "fermata",
    "slur",
    "tie",
    "tuplet",
    "credit",
    "identification",
    "bookmark",
    "link",
}


def remove_unwanted(elem):
    for child in list(elem):
        if child.tag in REMOVE_TAGS:
            elem.remove(child)
        else:
            remove_unwanted(child)


def remove_empty_voice(measure):
    voices = {}

    for note in measure.findall("note"):
        v = note.find("voice")
        if v is None:
            continue

        voice = v.text

        if voice not in voices:
            voices[voice] = 0

        if note.find("rest") is None:
            voices[voice] += 1

    if not voices:
        return

    keep_voice = max(voices, key=voices.get)

    for note in list(measure.findall("note")):
        v = note.find("voice")
        if v is not None and v.text != keep_voice:
            measure.remove(note)


def remove_empty_staff(measure):

    staffs = {}

    for note in measure.findall("note"):

        staff = note.find("staff")

        if staff is None:
            continue

        s = staff.text

        if s not in staffs:
            staffs[s] = 0

        if note.find("rest") is None:
            staffs[s] += 1

    if not staffs:
        return

    keep_staff = max(staffs, key=staffs.get)

    for note in list(measure.findall("note")):

        staff = note.find("staff")

        if staff is not None and staff.text != keep_staff:
            measure.remove(note)


def clean_musicxml(input_file, output_file):

    tree = ET.parse(input_file)
    root = tree.getroot()

    remove_unwanted(root)

    for part in root.findall("part"):
        for measure in part.findall("measure"):
            remove_empty_voice(measure)
            remove_empty_staff(measure)

    tree.write(output_file, encoding="utf-8", xml_declaration=True)

    print("Saved:", output_file)


if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("Usage:")
        print("python clean_musicxml.py input.musicxml output.musicxml")
        sys.exit()

    clean_musicxml(sys.argv[1], sys.argv[2])