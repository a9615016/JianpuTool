from music21 import converter, stream, note, meter
import copy
import sys
import xml.etree.ElementTree as ET


VERSION = "######## USING V84 PURE JIANPU XML SANITIZER ########"


# jianpu_ly 最安全節奏
GRID = [
    4.0,
    2.0,
    1.0,
    0.5,
    0.25,
    0.125
]


def quantize(x):

    x=float(x)

    return min(
        GRID,
        key=lambda y:abs(y-x)
    )



def extract_clean(score):

    print("extract notes")

    result=[]


    for n in score.recurse().notesAndRests:

        x=copy.deepcopy(n)


        # remove all notation

        x.expressions=[]

        x.articulations=[]

        x.lyrics=[]

        x.tie=None


        # remove voice

        if hasattr(x,"voice"):
            x.voice=None



        dur=float(
            x.duration.quarterLength
        )


        if dur<=0:
            continue


        x.duration.quarterLength = quantize(dur)


        result.append(x)


    return result




def rebuild_score(notes):

    print("PURE REBUILD")


    score=stream.Score()

    part=stream.Part()


    part.insert(
        0,
        meter.TimeSignature("4/4")
    )


    measure_no=1

    measure=stream.Measure(
        number=measure_no
    )


    beat=0.0



    for n in notes:


        remain_note=float(
            n.duration.quarterLength
        )


        while remain_note>0:


            space=4.0-beat


            take=min(
                space,
                remain_note
            )


            new=copy.deepcopy(n)


            new.duration.quarterLength=take


            # remove offset

            new.offset=0


            measure.append(new)


            beat+=take

            remain_note-=take



            if beat>=3.999:


                part.append(measure)


                measure_no+=1


                measure=stream.Measure(
                    number=measure_no
                )


                beat=0



    # last measure fill


    if beat>0:

        r=note.Rest()

        r.duration.quarterLength=4-beat

        measure.append(r)


        part.append(measure)



    score.append(part)


    return score




def check(score):

    print("FINAL CHECK")


    for m in score.parts[0].getElementsByClass(
        "Measure"
    ):


        total=sum(
            float(x.duration.quarterLength)
            for x in m.notesAndRests
        )


        print(
            "Measure",
            m.number,
            total
        )


        if abs(total-4)>0.001:

            raise Exception(
                "BAD MEASURE "
                +str(m.number)
            )


    print("ALL MEASURES SAFE")




def sanitize_xml(path):

    print("sanitize xml")


    tree=ET.parse(path)

    root=tree.getroot()


    # force divisions

    for d in root.iter():

        if d.tag.endswith("divisions"):

            d.text="4"



    # remove unwanted tags

    remove_tags=[
        "beam",
        "tie",
        "notations",
        "voice",
        "backup",
        "forward"
    ]


    for parent in root.iter():

        for child in list(parent):

            tag=child.tag.split("}")[-1]

            if tag in remove_tags:

                parent.remove(child)



    tree.write(
        path,
        encoding="utf-8",
        xml_declaration=True
    )




def clean(inp,out):


    print("================")
    print(VERSION)
    print("================")


    old=converter.parse(inp)


    notes=extract_clean(old)


    new=rebuild_score(notes)


    check(new)


    print("WRITE")


    new.write(
        "musicxml",
        fp=out
    )


    sanitize_xml(out)


    print("DONE")
    print(out)





if __name__=="__main__":


    if len(sys.argv)<3:

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit()


    clean(
        sys.argv[1],
        sys.argv[2]
    )