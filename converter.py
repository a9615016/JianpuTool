```python
import os
i
mport subprocess
import tempfile
from pathlib import Path


def convert_musicxml(musicxml_file):

    try:

        # Render Linux 沒有 TEMP
        temp_dir = tempfile.gettempdir()

        input_file = Path(musicxml_file)

        name = input_file.stem

        ly_file = Path(temp_dir) / f"{name}.ly"
        pdf_file = Path(temp_dir) / f"{name}.pdf"


        # MusicXML -> LilyPond
        cmd1 = [
            "python",
            "-m",
            "jianpu_ly",
            str(input_file)
        ]


        result = subprocess.run(
            cmd1,
            capture_output=True,
            text=True
        )


        if result.returncode != 0:
            raise Exception(
                "jianpu-ly error:\n"
                + result.stderr
            )


        # 寫入 ly
        with open(
            ly_file,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(result.stdout)



        # LilyPond -> PDF

        cmd2 = [
            "lilypond",
            "-fpdf",
            "-o",
            str(pdf_file.with_suffix("")),
            str(ly_file)
        ]


        result2 = subprocess.run(
            cmd2,
            capture_output=True,
            text=True
        )


        if result2.returncode != 0:

            raise Exception(
                "LilyPond error:\n"
                + result2.stderr
            )


        if not pdf_file.exists():

            raise Exception(
                "PDF沒有產生"
            )


        return str(pdf_file)


    except Exception as e:

        print("CONVERTER ERROR:")
        print(e)

        raise e

