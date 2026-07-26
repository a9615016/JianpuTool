import sys
import os
import music21
import xml.etree.ElementTree as ET


VERSION = "CLEAN VERSION 20260726 V7"


def remove_illegal_note_types(xml_file):

    print("remove illegal note types")

    tree = ET.parse(xml_file)
    root = tree.getroot()

    count = 0

    for elem in root.iter("type"):

        if elem.text == "128th":
            elem.text = "64th"
            count += 1

    tree.write(
        xml_file,
        encoding="utf-8",
        xml_declaration=True
    )

    print(
        "converted 128th:",
        count
    )



def clean_musicxml(input_file, output_file):

    print(VERSION)
    print("input:", input_file)


    score = music21.converter.parse(
        input_file
    )


    print("remove voices")

    for part in score.parts:
        for n in part.recurse():

            if hasattr(n, "voice"):
                n.voice = None



    print("remove chords")

    for c in list(
        score.recurse().getElementsByClass("Chord")
    ):

        if len(c.notes) > 0:

            c.activeSite.replace(
                c,
                c.notes[0]
            )



    print("remove grace")

    for n in score.recurse().notes:

        try:
            if n.duration.isGrace:
                n.duration.quarterLength = 0.25

        except:
            pass



    print("fix duration")

    for n in score.recurse().notes:

        q = n.duration.quarterLength


        # 禁止128分音符以下
        if q < 0.0625:

            n.duration.quarterLength = 0.0625



    print("remove tuplets")

    for n in score.recurse().notes:

        if n.duration.tuplets:

            n.duration.tuplets = []



    print("rebuild measures")

    score.makeMeasures(
        inPlace=True
    )



    print("fix bars")


    # 4/4 每小節 4拍

    target = 4.0


    for part in score.parts:

        for m in part.getElementsByClass("Measure"):


            length = m.duration.quarterLength


            # 超過小節

            if length > target:


                print(
                    "trim measure",
                    m.number,
                    length
                )


                remain = target


                for n in list(
                    m.notesAndRests
                ):

                    if remain <= 0:

                        m.remove(n)


                    else:

                        if n.duration.quarterLength > remain:

                            n.duration.quarterLength = remain


                        remain -= n.duration.quarterLength



            # 不足補休止

            elif length < target:


                diff = target - length


                r = music21.note.Rest()

                r.duration.quarterLength = diff


                m.insert(
                    m.duration.quarterLength,
                    r
                )



    print("final cleanup")


    for n in score.recurse().notes:

        n.duration.tuplets = []


        # 再保險一次

        if n.duration.quarterLength < 0.0625:

            n.duration.quarterLength = 0.0625



    print("write")


    score.write(
        "musicxml",
        fp=output_file
    )


    # 直接修 MusicXML

    remove_illegal_note_types(
        output_file
    )


    print(
        "done:",
        output_file
    )



if __name__ == "__main__":


    if len(sys.argv) < 2:

        print(
            "python clean_musicxml.py input.musicxml [output.musicxml]"
        )

        exit()



    input_file = sys.argv[1]


    if len(sys.argv) >= 3:

        output_file = sys.argv[2]

    else:

        output_file = (
            os.path.splitext(input_file)[0]
            +
            "_clean.musicxml"
        )



    clean_musicxml(
        input_file,
        output_file
    )