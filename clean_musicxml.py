import sys
import os
import xml.etree.ElementTree as ET
from fractions import Fraction


VERSION = "CLEAN VERSION 20260726 V18"


NS = "http://www.musicxml.org/ns/musicxml"


def qname(tag):
    return "{%s}%s" % (NS, tag)



def quantize_duration(value, old_div):

    if old_div == 0:
        return value

    beats = Fraction(value, old_div)

    unit = Fraction(1,4)

    result = round(beats / unit) * unit

    return int(result * 16)



def force_44(root):

    print("force time signature 4/4")


    for measure in root.iter(qname("measure")):


        attributes = measure.find(
            qname("attributes")
        )


        if attributes is None:

            attributes = ET.SubElement(
                measure,
                qname("attributes")
            )


        time = attributes.find(
            qname("time")
        )


        if time is None:

            time = ET.SubElement(
                attributes,
                qname("time")
            )


        beats = time.find(
            qname("beats")
        )


        if beats is None:

            beats = ET.SubElement(
                time,
                qname("beats")
            )


        beats.text = "4"



        beat_type = time.find(
            qname("beat-type")
        )


        if beat_type is None:

            beat_type = ET.SubElement(
                time,
                qname("beat-type")
            )


        beat_type.text = "4"



def clean(input_file, output_file):


    print(VERSION)
    print("input:", input_file)



    tree = ET.parse(input_file)

    root = tree.getroot()



    print("remove voices")


    for voice in root.iter(qname("voice")):

        for parent in root.iter():

            if voice in list(parent):

                parent.remove(voice)

                break




    print("remove chords")


    for chord in root.iter(qname("chord")):

        for parent in root.iter():

            if chord in list(parent):

                parent.remove(chord)

                break




    print("remove grace")


    for grace in root.iter(qname("grace")):

        for parent in root.iter():

            if grace in list(parent):

                parent.remove(grace)

                break




    force_44(root)



    print("quantize durations")


    old_div = 1


    d = root.find(
        ".//" + qname("divisions")
    )


    if d is not None:

        old_div = int(d.text)



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




    print("repair measure length")


    limit = 64



    for measure in root.iter(qname("measure")):


        total = 0


        notes=[]


        for note in measure.findall(
            qname("note")
        ):


            dur = note.find(
                qname("duration")
            )


            if dur is not None:

                try:

                    d=int(dur.text)

                    total += d

                    notes.append(
                        (note,d)
                    )

                except:

                    pass



        if total > limit:


            print(
                "fix measure",
                measure.attrib.get("number"),
                total
            )


            overflow = total-limit



            for note,d in reversed(notes):


                if overflow <=0:

                    break



                newd=d-overflow



                if newd>0:

                    note.find(
                        qname("duration")
                    ).text=str(newd)

                    overflow=0


                else:

                    note.find(
                        qname("duration")
                    ).text="1"

                    overflow-=d




    print("force divisions = 16")


    for div in root.iter(
        qname("divisions")
    ):

        div.text="16"




    print("write")


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

        base=os.path.splitext(inp)[0]

        out=base+"_clean.musicxml"



    clean(
        inp,
        out
    )