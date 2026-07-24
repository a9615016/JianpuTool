import xml.etree.ElementTree as ET
import sys


def clean_musicxml(input_file, output_file):

    print("開始 clean MusicXML")


    tree = ET.parse(input_file)
    root = tree.getroot()


    def tag(x):
        return x.split("}")[-1]


    # 移除造成 jianpu_ly 錯誤元素

    remove = {
        "backup",
        "forward",
        "grace",
        "notations",
        "accidental",
        "tie",
        "lyric",
        "chord"
    }


    def clean(parent):

        for child in list(parent):

            if tag(child.tag) in remove:

                parent.remove(child)

            else:

                clean(child)


    clean(root)



    # 所有 note 強制單聲部

    for note in root.iter():

        if tag(note.tag) == "note":

            has_pitch = False

            for child in note:

                if tag(child.tag) == "pitch":

                    has_pitch = True



            # 移除複雜標記

            for child in list(note):

                if tag(child.tag) in [
                    "voice",
                    "staff"
                ]:

                    note.remove(child)



            voice = ET.Element(
                "voice"
            )

            voice.text="1"


            # 放回 voice

            note.append(voice)



    # octave 固定

    for octave in root.iter():

        if tag(octave.tag)=="octave":

            octave.text="4"



    # 移除空白

    for e in root.iter():

        if e.text:

            e.text=e.text.strip()



    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True
    )


    print("clean完成")
    print(output_file)



if __name__=="__main__":

    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )