import os
import uuid
import shutil
import subprocess

from music21 import converter



def clean_musicxml(input_xml):

    """
    MusicXML 清理
    保留第一聲部
    """

    score = converter.parse(
        input_xml
    )


    # 多聲部只留第一個
    if len(score.parts) > 1:

        score = score.parts[0]


    output_xml = (
        "/tmp/"
        + str(uuid.uuid4())
        + "_clean.musicxml"
    )


    score.write(
        "musicxml",
        fp=output_xml
    )


    return output_xml





def convert_musicxml(xml_file):

    uid = str(uuid.uuid4())


    temp_dir = "/tmp"


    clean_xml = (
        f"{temp_dir}/{uid}_clean.musicxml"
    )


    ly_file = (
        f"{temp_dir}/{uid}.ly"
    )


    pdf_file = (
        f"{temp_dir}/{uid}.pdf"
    )



    print(
        "INPUT XML:",
        xml_file
    )



    # =====================
    # 1. MusicXML 清理
    # =====================

    try:

        clean_xml = clean_musicxml(
            xml_file
        )


        print(
            "CLEAN XML:",
            clean_xml
        )


    except Exception as e:

        raise Exception(
            "MusicXML clean failed: "
            + str(e)
        )



    # =====================
    # 2. jianpu_ly
    # =====================

    try:

        with open(
            ly_file,
            "w",
            encoding="utf-8"
        ) as f:


            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "jianpu_ly",
                    clean_xml
                ],
                stdout=f,
                stderr=subprocess.PIPE,
                text=True
            )


        if result.returncode != 0:

            print(
                result.stderr
            )

            raise Exception(
                "jianpu_ly failed"
            )


        print(
            "LY:",
            ly_file
        )


    except Exception as e:

        raise Exception(
            str(e)
        )



    # =====================
    # 3. LilyPond PDF
    # =====================

    try:

        result = subprocess.run(
            [
                "lilypond",
                "-o",
                pdf_file.replace(
                    ".pdf",
                    ""
                ),
                ly_file
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )


        if result.returncode != 0:

            print(
                result.stderr
            )

            raise Exception(
                "lilypond failed"
            )


        print(
            "PDF:",
            pdf_file
        )


    except Exception as e:

        raise Exception(
            str(e)
        )



    return pdf_file
