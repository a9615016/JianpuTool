import sys
import os
import xml.etree.ElementTree as ET
from fractions import Fraction


VERSION = "CLEAN VERSION 20260726 V16"


def qname(tag):
    return "{http://www.musicxml.org/ns/musicxml}" + tag


def quantize_duration(value, old_div):

    if old_div == 0:
        return value

    beats = Fraction(value, old_div)

    # 四分音符
    unit = Fraction(1, 4)

    result = round(beats / unit) * unit

    # divisions = 16
    return int(result * 16)



def clean(input_file, output_file):

    print(VERSION)
    print("input:", input_file)


    tree = ET.parse(input_file)
    root = tree.getroot()


    # 保存原始 divisions
    old_div = 1

    d = root.find(".//" + qname("divisions"))

    if d is not None:
        old_div = int(d.text)



    print("remove voices")

    for voice in root.iter(qname("voice")):

        parent = None

        for p in root.iter():

            if voice in list(p):
                parent = p
                break


        if parent is not None:
            parent.remove(voice)



    print("remove chords")

    for chord in root.iter(qname("chord")):

        for p in root.iter():

            if chord in list(p):
                p.remove(chord)
                break



    print("remove grace")

    for grace in root.iter(qname("grace")):

        for p in root.iter():

            if grace in list(p):
                p.remove(grace)
                break




    print("quantize durations")


    for dur in root.iter(qname("duration")):

        try:

            value = int(dur.text)

            dur.text = str(
                quantize_duration(
                    value,
                    old_div
                )
            )

        except:

            pass





    print("repair measures")


    # 4/4
    measure_limit = 64



    for measure in root.iter(qname("measure")):


        total = 0

        notes = []


        for note in measure.findall(qname("note")):


            dur = note.find(qname("duration"))


            if dur is not None:

                try:

                    d = int(dur.text)

                    total += d

                    notes.append(
                        (note, d)
                    )

                except:

                    pass




        if total != measure_limit:


            print(
                "repair measure",
                measure.attrib.get("number"),
                "duration:",
                total
            )



            diff = measure_limit - total



            # 太短，補最後音符

            if diff > 0:


                if notes:

                    note, d = notes[-1]

                    note.find(
                        qname("duration")
                    ).text = str(
                        d + diff
                    )



            # 太長，削減

            elif diff < 0:


                overflow = -diff


                for note, d in reversed(notes):


                    if overflow <= 0:
                        break



                    newd = d - overflow



                    if newd > 0:


                        note.find(
                            qname("duration")
                        ).text = str(newd)

                        overflow = 0



                    else:


                        note.find(
                            qname("duration")
                        ).text = "1"

                        overflow -= d





    print("final cleanup")



    # 最後才設定 divisions=16

    print("force divisions = 16")


    for div in root.iter(qname("divisions")):

        div.text = "16"




    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True
    )


    print("done:")
    print(output_file)




if __name__ == "__main__":


    if len(sys.argv) < 2:

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit()



    inp = sys.argv[1]


    if len(sys.argv) >= 3:

        out = sys.argv[2]


    else:

        base = os.path.splitext(inp)[0]

        out = base + "_clean.musicxml"



    clean(inp, out)