import os
import tempfile
import subprocess


def convert_musicxml(input_file):

    # Render Linux 暫存資料夾
    temp_dir = tempfile.gettempdir()

    print("TEMP DIR:", temp_dir)


    # .ly 檔
    ly_file = os.path.join(
        temp_dir,
        "jianpu_output.ly"
    )


    # PDF輸出
    pdf_file = os.path.join(
        temp_dir,
        "jianpu_output.pdf"
    )


    try:

        # =========================
        # MusicXML → LilyPond
        # =========================

        cmd1 = [
            "python",
            "-m",
            "jianpu_ly",
            input_file
        ]


        result = subprocess.run(
            cmd1,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )


        if result.returncode != 0:
            raise Exception(
                "jianpu_ly error:\n"
                + result.stderr
            )


        with open(
            ly_file,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(result.stdout)



        print("LY FILE:")
        print(ly_file)



        # =========================
        # LilyPond → PDF
        # =========================

        cmd2 = [
            "lilypond",
            "-o",
            os.path.join(
                temp_dir,
                "jianpu_output"
            ),
            ly_file
        ]


        result2 = subprocess.run(
            cmd2,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )


        print(result2.stdout)
        print(result2.stderr)



        if not os.path.exists(pdf_file):

            raise Exception(
                "LilyPond PDF產生失敗\n"
                + result2.stderr
            )



        return pdf_file



    except Exception as e:

        print(
            "CONVERT ERROR:",
            str(e)
        )

        raise e