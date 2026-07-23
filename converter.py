import os
import subprocess
import uuid
import tempfile


print("CONVERTER MVP VERSION")


LILYPOND = "lilypond"



def convert_musicxml(
    musicxml_file
):

    uid = str(uuid.uuid4())


    # Render Linux 暫存目錄
    temp_dir = tempfile.gettempdir()


    ly_file = os.path.join(
        temp_dir,
        f"{uid}.ly"
    )


    pdf_file = os.path.join(
        temp_dir,
        f"{uid}.pdf"
    )


    print("Input MusicXML:")
    print(musicxml_file)


    print("Generate LY:")
    print(ly_file)



    # ==========================
    # MusicXML → jianpu ly
    # ==========================

    cmd1 = [
        "python",
        "-m",
        "jianpu_ly",
        musicxml_file
    ]


    result = subprocess.run(
        cmd1,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )


    if result.returncode != 0:

        print(result.stderr)

        raise Exception(
            "jianpu_ly failed"
        )


    with open(
        ly_file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            result.stdout
        )



    print(
        "LY generated"
    )



    # ==========================
    # LilyPond → PDF
    # ==========================


    cmd2 = [
        LILYPOND,
        "-o",
        os.path.join(
            temp_dir,
            uid
        ),
        ly_file
    ]


    result2 = subprocess.run(
        cmd2,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )


    print(
        result2.stdout
    )


    print(
        result2.stderr
    )



    if result2.returncode != 0:

        raise Exception(
            "LilyPond failed"
        )



    generated_pdf = os.path.join(
        temp_dir,
        uid + ".pdf"
    )


    if not os.path.exists(
        generated_pdf
    ):

        raise Exception(
            "PDF not created"
        )



    print(
        "PDF created:",
        generated_pdf
    )


    return generated_pdf
