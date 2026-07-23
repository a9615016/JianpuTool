import os
import subprocess
import tempfile
import uuid


LILYPOND = "lilypond"


def convert_musicxml(xml_file):

    uid = str(uuid.uuid4())

    # Windows / Linux 自動判斷
    temp_dir = tempfile.gettempdir()

    work_dir = os.path.join(
        temp_dir,
        "jianputool_" + uid
    )

    os.makedirs(
        work_dir,
        exist_ok=True
    )


    print("WORK DIR:", work_dir)


    ly_file = os.path.join(
        work_dir,
        "output.ly"
    )

    pdf_file = os.path.join(
        work_dir,
        "output.pdf"
    )


    #
    # MusicXML → jianpu.ly
    #
    print("Running jianpu_ly...")


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
                xml_file
            ],
            stdout=f,
            stderr=subprocess.PIPE,
            text=True
        )


    if result.returncode != 0:

        print(result.stderr)

        raise Exception(
            "jianpu_ly failed"
        )


    print("LY generated:", ly_file)



    #
    # 修正 LilyPond tempo
    #
    with open(
        ly_file,
        "r",
        encoding="utf-8"
    ) as f:

        ly = f.read()


    ly = ly.replace(
        "tempoWholesPerMinute = #(ly:make-moment 84 4)",
        "tempoWholesPerMinute = #84"
    )


    with open(
        ly_file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(ly)



    #
    # LilyPond PDF
    #
    print("Running LilyPond...")


    result = subprocess.run(
        [
            LILYPOND,
            "--pdf",
            "-o",
            work_dir,
            ly_file
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )


    if result.returncode != 0:

        print(result.stderr)

        raise Exception(
            "LilyPond failed"
        )


    #
    # 找 PDF
    #
    generated_pdf = os.path.join(
        work_dir,
        "output.pdf"
    )


    if not os.path.exists(generated_pdf):

        raise Exception(
            "PDF not generated"
        )


    print(
        "PDF OK:",
        generated_pdf
    )


    return generated_pdf
