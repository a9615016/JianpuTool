import os
import tempfile
import subprocess


def convert_musicxml(input_file):

    temp_dir = tempfile.gettempdir()

    print("TEMP DIR:", temp_dir)


    ly_file = os.path.join(
        temp_dir,
        "jianpu_output.ly"
    )


    pdf_file = os.path.join(
        temp_dir,
        "jianpu_output.pdf"
    )


    try:

        # =========================
        # MusicXML → jianpu ly
        # =========================

        cmd1 = [
            "python",
            "-m",
            "jianpu_ly",
            input_file
        ]


        print("RUN:")
        print(cmd1)


        result1 = subprocess.run(
            cmd1,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )


        print("JIANPU-LY ERROR:")
        print(result1.stderr)


        if result1.returncode != 0:

            raise Exception(
                "jianpu-ly failed\n"
                + result1.stderr
            )


        with open(
            ly_file,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(result1.stdout)



        print("LY CREATED:")
        print(ly_file)



        # =========================
        # LilyPond → PDF
        # =========================

        output_base = os.path.join(
            temp_dir,
            "jianpu_output"
        )


        cmd2 = [
            "lilypond",
            "-o",
            output_base,
            ly_file
        ]


        print("RUN LILYPOND:")
        print(cmd2)


        result2 = subprocess.run(
            cmd2,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )


        print("================")
        print("LILYPOND OUTPUT")
        print("================")
        print(result2.stdout)


        print("================")
        print("LILYPOND ERROR")
        print("================")
        print(result2.stderr)



        if not os.path.exists(pdf_file):

            raise Exception(
                "PDF not created\n\n"
                + result2.stderr
            )



        return pdf_file



    except Exception as e:

        print("================")
        print("CONVERT ERROR")
        print("================")
        print(str(e))

        raise e