import sys
import os
import xml.etree.ElementTree as ET
from fractions import Fraction


VERSION = "CLEAN VERSION 20260726 V17"


NS = "http://www.musicxml.org/ns/musicxml"


def qname(tag):
    return "{%s}%s" % (NS, tag)



def quantize_duration(value, old_div):

    if old_div == 0:
        return value

    beats = Fraction(value, old_div)

    unit = Fraction(1, 4)

    result = round(beats / unit) * unit

    return int(result * 16)



def add_tie(note, tie_type):

    tie = ET.SubElement(
        note,
        qname("tie")
    )

    tie.set(
        "type",
        tie_type
    )


    notations = note.find(
        qname("notations")
    )

    if notations is None:

        notations = ET.SubElement(
            note,
            qname("notations")
        )


    tied = ET.SubElement(
        notations,
        qname("tied")
    )

    tied.set(
        "type",
        tie_type
    )



def clean(input_file, output_file):

    print(VERSION)
    print("input:", input_file)


    tree = ET.parse(input_file)

    root = tree.getroot()


    old_div = 1

    d = root.find(
        ".//" + qname("divisions")
    )

    if d is not None:
        old_div = int(d.text)



    print("remove voices")

    for voice in root.iter(qname("voice")):

        for p in root.iter():

            if voice in list(p):

                p.remove(voice)

                break




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

            dur.text = str(
                quantize_duration(
                    int(dur.text),
                    old_div
                )
            )

        except:

            pass





    print("split cross measure notes")


    measure_limit = 64



    for measure in root.iter(qname("measure")):


        total = 0


        notes = list(
            measure.findall(
                qname("note")
            )
        )


        for note in notes:


            dur = note.find(
                qname("duration")
            )


            if dur is None:
                continue


            try:

                d = int(dur.text)

            except:

                continue



            if total + d > measure_limit:


                first = measure_limit - total

                second = d - first



                print(
                    "split note in measure",
                    measure.attrib.get("number"),
                    d,
                    "=>",
                    first,
                    "+",
                    second
                )



                # 原 note 改前半

                dur.text = str(first)

                add_tie(
                    note,
                    "start"
                )



                # 複製後半 note

                new_note = ET.fromstring(
                    ET.tostring(note)
                )


                new_dur = new_note.find(
                    qname("duration")
                )

                new_dur.text = str(second)


                add_tie(
                    new_note,
                    "stop"
                )


                measure.append(
                    new_note
                )


                total = measure_limit



            else:

                total += d





    print("repair measure length")



    for measure in root.iter(qname("measure")):


        total = 0


        for note in measure.findall(qname("note")):

            dur = note.find(qname("duration"))

            if dur is not None:

                try:
                    total += int(dur.text)

                except:
                    pass



        if total != 64:

            print(
                "measure duration:",
                measure.attrib.get("number"),
                total
            )




    print("force divisions = 16")


    for div in root.iter(qname("divisions")):

        div.text="16"




    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True
    )


    print("done:")
    print(output_file)





if __name__=="__main__":


    if len(sys.argv)<2:

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit()



    inp=sys.argv[1]


    if len(sys.argv)>=3:

        out=sys.argv[2]

    else:

        out=os.path.splitext(inp)[0]+"_clean.musicxml"



    clean(
        inp,
        out
    )