import os
import uuid
import shutil
import subprocess
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse

from music21 import converter, meter


app = FastAPI()


BASE_DIR = "outputs"
os.makedirs(BASE_DIR, exist_ok=True)


@app.get("/")
def home():

    return HTMLResponse(
        """
        <html>
        <body>

        <h2>JianpuTool v26</h2>

        <p>MP3 / MIDI / MusicXML → Jianpu PDF</p>

        <form action="/upload"
        method="post"
        enctype="multipart/form-data">

        <input type="file" name="file">

        <button type="submit">
        Convert
        </button>

        </form>

        </body>
        </html>
        """
    )



# =========================
# MusicXML 修正核心
# =========================

def fix_musicxml(src, dst):

    print("開始修正 MusicXML")

    score = converter.parse(src)


    # 強制 4/4
    for part in score.parts:

        part.insert(
            0,
            meter.TimeSignature("4/4")
        )


    # 移除複雜節奏
    for n in score.recurse().notesAndRests:


        if hasattr(n, "duration"):

            # 移除 tuplets
            n.duration.tuplets = []


            # 防止奇怪 duration
            if n.duration.quarterLength > 4:
                n.duration.quarterLength = 4



    # 重新量化
    score.quantize(
        quarterLengthDivisors=[
            1,
            2,
            4,
            8,
            16
        ]
    )


    # 寫出新的 MusicXML

    score.write(
        "musicxml",
        fp=dst
    )


    print(
        "MusicXML 修正完成:",
        dst
    )





# =========================
# Upload
# =========================


@app.post("/upload")
async def upload(
        file: UploadFile = File(...)
):


    job_id = str(uuid.uuid4())

    work = os.path.join(
        BASE_DIR,
        job_id
    )

    os.makedirs(work)


    input_file=os.path.join(
        work,
        file.filename
    )


    with open(
        input_file,
        "wb"
    ) as f:

        shutil.copyfileobj(
            file.file,
            f
        )


    print("================")
    print("收到:")
    print(file.filename)
    print("================")



    try:


        # --------------------
        # 如果輸入 MusicXML
        # --------------------

        if file.filename.endswith(
            ".musicxml"
        ):

            musicxml=input_file



        # --------------------
        # MIDI
        # --------------------

        elif file.filename.endswith(
            ".mid"
        ):

            musicxml=os.path.join(
                work,
                "input.musicxml"
            )


            subprocess.run(
                [
                    "python",
                    "midi_to_musicxml.py",
                    input_file,
                    musicxml
                ],
                check=True
            )


        # --------------------
        # MP3
        # --------------------

        else:


            midi=os.path.join(
                work,
                "melody.mid"
            )


            subprocess.run(
                [
                    "python",
                    "basicpitch_convert.py",
                    input_file,
                    midi
                ],
                check=True
            )


            musicxml=os.path.join(
                work,
                "input.musicxml"
            )


            subprocess.run(
                [
                    "python",
                    "midi_to_musicxml.py",
                    midi,
                    musicxml
                ],
                check=True
            )



        # =====================
        # 關鍵修正
        # =====================

        fixed=os.path.join(
            work,
            "fixed.musicxml"
        )


        fix_musicxml(
            musicxml,
            fixed
        )



        # =====================
        # jianpu_ly
        # =====================


        ly=os.path.join(
            work,
            "score.ly"
        )


        print(
            "開始 jianpu_ly"
        )


        with open(
            ly,
            "w",
            encoding="utf-8"
        ) as out:


            result=subprocess.run(
                [
                    "python",
                    "-m",
                    "jianpu_ly",
                    fixed
                ],
                stdout=out,
                stderr=subprocess.PIPE,
                text=True
            )


        if result.returncode !=0:

            return {
                "error":
                "jianpu_ly failed",
                "log":
                result.stderr
            }




        # =====================
        # LilyPond
        # =====================


        print(
            "開始 LilyPond"
        )


        result=subprocess.run(
            [
                "lilypond",
                "-o",
                os.path.join(
                    work,
                    "jianpu"
                ),
                ly
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )


        print(
            result.stdout
        )


        pdf=os.path.join(
            work,
            "jianpu.pdf"
        )


        if not os.path.exists(pdf):

            return {
                "error":
                "PDF產生失敗",
                "log":
                result.stdout
            }



        return FileResponse(
            pdf,
            media_type="application/pdf",
            filename="jianpu.pdf"
        )



    except Exception as e:


        return {
            "error":
            str(e)
        }