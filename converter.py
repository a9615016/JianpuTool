import os
import subprocess
import tempfile
import shutil
import uuid


def convert_musicxml(xml_file):

    print("START MusicXML convert")

    # =====================================
    # 每首歌曲獨立暫存資料夾
    # =====================================

    song_name = os.path.splitext(
        os.path.basename(xml_file)
    )[0]


    temp_dir = tempfile.gettempdir()


    work_dir = os.path.join(
        temp_dir,
        "jianputool",
        song_name + "_" + str(uuid.uuid4())[:8]
    )


    os.makedirs(
        work_dir,
        exist_ok=True
    )


    print(
        "WORK DIR:",
        work_dir
    )



    # =====================================
    # MusicXML -> LilyPond
    # =====================================

    ly_file = os.path.join(
        work_dir,
        "output.ly"
    )


    with open(
        ly_file,
        "w",
        encoding="utf-8"
    ) as f:


        subprocess.run(
            [
                "python",
                "-m",
                "jianpu_ly",
                xml_file
            ],
            stdout=f,
            stderr=subprocess.STDOUT,
            check=True
        )



    print(
        "LY:",
        ly_file
    )



    # =====================================
    # LilyPond -> PDF
    # =====================================

    pdf_output = os.path.join(
        work_dir,
        "jianpu"
    )


    subprocess.run(
        [
            "lilypond",
            "-o",
            pdf_output,
            ly_file
        ],
        check=True
    )



    temp_pdf = pdf_output + ".pdf"



    if not os.path.exists(temp_pdf):

        raise Exception(
            "PDF not generated"
        )



    # =====================================
    # 輸出到原歌曲資料夾
    # =====================================

    output_dir = os.path.dirname(
        xml_file
    )


    final_pdf = os.path.join(
        output_dir,
        song_name + "_jianpu.pdf"
    )



    shutil.copy(
        temp_pdf,
        final_pdf
    )


    print(
        "DONE:",
        final_pdf
    )


    return final_pdf