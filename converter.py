import os
import subprocess
import tempfile
import uuid


def convert_musicxml(xml_file):

    uid = str(uuid.uuid4())

    # Windows / Linux 通用暫存路徑
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
        "jianpu.ly"
    )


    print("MusicXML -> Jianpu")


    # MusicXML 轉 jianpu ly
    with open(
        ly_file,
        "w",
        encoding="utf-8"
    ) as output:

        result = subprocess.run(
            [
                "python",
                "-m",
                "jianpu_ly",
                xml_file
            ],
            stdout=output,
            stderr=subprocess.PIPE,
            text=True
        )


    if result.returncode != 0:

        print(result.stderr)

        raise Exception(
            "jianpu_ly convert failed"
        )


    print(
        "LY created:",
        ly_file
    )


    # 修正 LilyPond tempo 問題
    with open(
        ly_file,
        "r",
        encoding="utf-8"
    ) as f:

        content = f.read()


    content = content.replace(
        "tempoWholesPerMinute = #(ly:make-moment 84 4)",
        "tempoWholesPerMinute = #84"
    )


    with open(
        ly_file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(content)



    print("LilyPond PDF")


    # Render Linux 使用 lilypond
    result = subprocess.run(
        [
            "lilypond",
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


    pdf_file = os.path.join(
        work_dir,
        "jianpu.pdf"
    )


    # 有些 LilyPond 會用 ly 名稱輸出
    if not os.path.exists(pdf_file):

        possible = os.path.join(
            work_dir,
            "jianpu.pdf"
        )

        if os.path.exists(possible):
            pdf_file = possible


    if not os.path.exists(pdf_file):

        files = os.listdir(work_dir)

        print(
            "Files:",
            files
        )

        raise Exception(
            "PDF not generated"
        )


    print(
        "PDF:",
        pdf_file
    )


    return pdf_file
