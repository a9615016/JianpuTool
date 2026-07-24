import xml.etree.ElementTree as ET
import sys


def clean_musicxml(input_file, output_file):

    print("讀取 MusicXML:", input_file)

    # =========================
    # 強制處理編碼
    # =========================

    with open(input_file, "rb") as f:
        data = f.read()

    try:
        text = data.decode("utf-8-sig")

    except:

        try:
            text = data.decode("utf-16")

        except:

            text = data.decode(
                "cp950",
                errors="ignore"
            )


    # =========================
    # XML 解析
    # =========================

    root = ET.fromstring(text)


    # =========================
    # 清理資料
    # =========================

    for elem in root.iter():

        tag = elem.tag.split("}")[-1]


        # 修正 octave
        if tag == "octave":

            try:

                value = int(elem.text)

                if value < 0 or value > 8:
                    elem.text = "4"

            except:

                elem.text = "4"



        # 修正 step
        if tag == "step":

            if elem.text not in [
                "A",
                "B",
                "C",
                "D",
                "E",
                "F",
                "G"
            ]:

                elem.text = "C"



        # 修正 voice
        if tag == "voice":

            if elem.text:

                if elem.text not in [
                    "1",
                    "2"
                ]:

                    elem.text = "1"



    # =========================
    # 輸出 UTF-8 MusicXML
    # =========================

    tree = ET.ElementTree(root)

    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True
    )


    print("clean完成:", output_file)



if __name__ == "__main__":


    if len(sys.argv) < 3:

        print(
            "使用方式:"
        )

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        exit()



    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )