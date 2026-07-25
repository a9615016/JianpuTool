import sys
import xml.etree.ElementTree as ET


REMOVE_TAGS = {
    "credit",
    "defaults",
    "direction",
    "print",
    "bookmark",
    "link",
    "sound",
    "listening",
    "grouping",
}


def strip_namespace(tag):
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def remove_grace(parent):
    remove = []

    for note in parent.findall(".//note"):
        has_grace = False

        for child in note:
            if strip_namespace(child.tag) == "grace":
                has_grace = True
                break

        if has_grace:
            remove.append(note)

    for note in remove:
        p = find_parent(parent, note)
        if p is not None:
            p.remove(note)


def remove_notations(root):

    for note in root.findall(".//note"):

        remove = []

        for child in note:

            name = strip_namespace(child.tag)

            if name == "notations":
                remove.append(child)

            elif name == "lyric":
                remove.append(child)

        for x in remove:
            note.remove(x)


def remove_simple_tags(root):

    for parent in root.iter():

        remove = []

        for child in list(parent):

            name = strip_namespace(child.tag)

            if name in REMOVE_TAGS:
                remove.append(child)

        for x in remove:
            parent.remove(x)


def find_parent(root, target):

    for parent in root.iter():

        for child in list(parent):

            if child is target:
                return parent

    return None


def clean(input_file, output_file):

    print("XML CLEANER")

    tree = ET.parse(input_file)

    root = tree.getroot()

    remove_simple_tags(root)

    remove_notations(root)

    remove_grace(root)

    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True
    )

    print("Saved:", output_file)


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage:")
        print("python clean_musicxml.py input.musicxml output.musicxml")
        sys.exit(1)

    input_file = sys.argv[1]

    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        output_file = input_file.replace(
            ".musicxml",
            "_clean.musicxml"
        )

    clean(
        input_file,
        output_file
    )