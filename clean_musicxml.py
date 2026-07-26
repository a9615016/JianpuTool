import sys
import os
import xml.etree.ElementTree as ET
from fractions import Fraction


VERSION = "CLEAN VERSION 20260726 V15"


def qname(tag):
    return "{http://www.musicxml.org/ns/musicxml}" + tag


def text(elem, tag):
    x = elem.find(qname(tag))
    if x is None:
        return None
    return x.text


def quantize_duration(value, old_div):

    if old_div == 0:
        return value

    # 轉成 quarter fraction
    beats = Fraction(value, old_div)

    # 四捨五入到 1/16 音符
    unit = Fraction(1,4)

    result = round(beats / unit) * unit

    # 新 divisions=16
    return int(result * 16)



def clean(input_file, output_file):

    print(VERSION)
    print("input:", input_file)

    tree = ET.parse(input_file)
    root = tree.getroot()


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



    print("force divisions = 16")


    for div in root.iter(qname("divisions")):
        div.text = "16"



    print("quantize durations")


    old_div = 1

    # 找原 divisions
    d = root.find(".//" + qname("divisions"))
    if d is not None:
        old_div = int(d.text)


    for dur in root.iter(qname("duration")):

        try:
            value=int(dur.text)
            dur.text=str(
                quantize_duration(
                    value,
                    old_div
                )
            )

        except:
            pass



    print("repair measures")


    # 4/4 每小節64
    measure_limit = 64


    for measure in root.iter(qname("measure")):

        total = 0

        notes=[]

        for note in measure.findall(qname("note")):

            dur = note.find(qname("duration"))

            if dur is not None:

                try:
                    d=int(dur.text)
                    total += d
                    notes.append((note,d))

                except:
                    pass


        if total > measure_limit:

            print(
                "fix measure",
                measure.attrib.get("number"),
                total
            )


            overflow = total - measure_limit


            for note,d in reversed(notes):

                if overflow<=0:
                    break


                newd=d-overflow


                if newd>0:
                    note.find(qname("duration")).text=str(newd)
                    overflow=0

                else:
                    note.find(qname("duration")).text="1"
                    overflow-=d



    print("final cleanup")


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


    clean(inp,out)