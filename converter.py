import os
import subprocess
import tempfile
import shutil


def convert_musicxml(xml_file):

    print("START MusicXML convert")

    # Linux(Render) / Windows 通用暫存資料夾
    temp_dir = tempfile.gettempdir()

    work_dir = os.path.join(
        temp_dir,
        "jianputool"
    )

    os.makedirs(
        work_dir,
        exist_ok=True
    )


    ly_file = os.path.join(
        work_dir,
        "output.ly"
    )


    pdf_output = os.path.join(
        work_dir,
        "jianpu"
    )


    # ==========================
    # MusicXML → LilyPond
    # ==========================

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


    print("LilyPond input:")
    print(ly_file)


    # ==========================
    # LilyPond → PDF
    # ==========================

    subprocess.run(
        [
            "lilypond",
            "-o",
            pdf_output,
            ly_file
        ],
        check=True
    )


    pdf_file = pdf_output + ".pdf"


    if not os.path.exists(pdf_file):

        raise Exception(
            "PDF not generated"
        )


    # 複製回專案輸出
    final_pdf = os.path.join(
        os.path.dirname(xml_file),
        "jianpu.pdf"
    )


    shutil.copy(
        pdf_file,
        final_pdf
    )


    print(
        "DONE:",
        final_pdf
    )


    return final_pdf