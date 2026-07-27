import sys
from music21 import converter, stream, meter, note, chord
from lxml import etree


print("================")
print("CLEAN MUSICXML V25 FINAL JIANPU COMPATIBLE")
print("================")


if len(sys.argv) < 3:
    print("usage:")
    print("python clean_musicxml.py input.musicxml output.musicxml")
    sys.exit(1)


input_file = sys.argv[1]
output_file = sys.argv[2]


print("read")

score = converter.parse(input_file)


# ==========================
# remove voices
# ==========================

print("remove voices")

for part in score.parts:
    for n in part.recurse():
        if hasattr(n, "voice"):
            n.voice = None



# ==========================
# remove chords
# ==========================

print("remove chords")

for part in score.parts:

    for element in list(part.recurse()):

        if isinstance(element, chord.Chord):

            new_note = note.Note(
                element.root().pitch
            )

            new_note.duration = element.duration

            element.activeSite.replace(
                element,
                new_note
            )



# ==========================
# remove notation
# ==========================

print("remove beams")

for n in score.recurse():

    if hasattr(n, "beams"):
        n.beams = None


print("remove ties")

for n in score.recurse():

    if hasattr(n, "tie"):
        n.tie = None



# ==========================
# force 4/4
# ==========================

print("force 4/4")

for part in score.parts:

    part.insert(
        0,
        meter.TimeSignature("4/4")
    )



# ==========================
# duration quantize
# ==========================

print("duration quantize")

for n in score.recurse().notesAndRests:

    q = n.duration.quarterLength

    allowed = [
        4,
        2,
        1,
        0.5,
        0.25
    ]

    closest = min(
        allowed,
        key=lambda x:abs(x-q)
    )

    n.duration.quarterLength = closest



# ==========================
# rebuild measures
# ==========================

print("rebuild measures")


new_score = stream.Score()


for part in score.parts:

    new_part = stream.Part()

    new_part.append(
        meter.TimeSignature("4/4")
    )

    for n in part.flatten().notesAndRests:

        new_part.append(n)

    new_part.makeMeasures(
        inPlace=True
    )

    new_score.append(new_part)



score = new_score



# ==========================
# check measures
# ==========================

for i,m in enumerate(score.parts[0].getElementsByClass("Measure")):

    print(
        "Measure",
        i+1,
        float(m.duration.quarterLength)
    )



# ==========================
# write temp
# ==========================

print("FINAL WRITE")

score.write(
    "musicxml",
    fp=output_file
)



# ==========================
# XML PURGE
# ==========================

print("XML PURGE")

tree = etree.parse(output_file)

root = tree.getroot()


# remove backup / forward
for tag in [
    "backup",
    "forward"
]:

    for node in root.xpath(".//" + tag):

        parent = node.getparent()

        if parent is not None:
            parent.remove(node)



# remove voices

for node in root.xpath(".//voice"):

    parent=node.getparent()

    if parent is not None:
        parent.remove(node)



# remove beams

for node in root.xpath(".//beam"):

    parent=node.getparent()

    if parent is not None:
        parent.remove(node)



# remove ties

for node in root.xpath(".//tie"):

    parent=node.getparent()

    if parent is not None:
        parent.remove(node)



tree.write(
    output_file,
    encoding="UTF-8",
    xml_declaration=True
)



print("================")
print("FINAL XML PURGE DONE")
print("DONE")
print(output_file)
print("================")