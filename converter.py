import os
import subprocess
import tempfile


def convert_musicxml(musicxml_file):

    # Render Linux / Windows 都支援
    temp_dir = tempfile.gettempdir()

    filename = os.path.splitext(
        os.path.basename(musicxml_file)
    )[0]


    # 輸出 ly
    ly_file = os.path.join(
        temp_dir,
        filename + "_jianpu.ly"
    )


    pdf_file = os.path.join(
        temp_dir,
        filename + "_jianpu.pdf"
    )


    print("MusicXML:", musicxml_file)
    print("LY:", ly_file)


    # MusicXML → jianpu ly
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
                musicxml_file
            ],
            stdout=f,
            stderr=subprocess.PIPE,
            text=True
        )


    if result.returncode != 0:

        raise Exception(
            "jianpu_ly error:\n"
            + result.stderr
        )


    # LilyPond → PDF

    result = subprocess.run(
        [
            "lilypond",
            "-o",
            os.path.join(
                temp_dir,
                filename + "_jianpu"
            ),
            ly_file
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )


    if result.returncode != 0:

        raise Exception(
            "lilypond error:\n"
            + result.stderr
        )


    if not os.path.exists(pdf_file):

        raise Exception(
            "PDF not generated"
        )


    return pdf_file