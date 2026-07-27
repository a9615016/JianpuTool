import os
import uuid
import shutil
import subprocess
from pathlib import Path

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse


# =========================
# 基本設定
# =========================

app = FastAPI(
    title="JianpuTool v26",
    version="26.0"
)


BASE_DIR = Path("/app")

OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


# =========================
# 首頁
# =========================

@app.get("/")
def home():

    return HTMLResponse("""
    <html>
    <head>
    <title>JianpuTool v26</title>
    </head>

    <body>

    <h1>JianpuTool v26</h1>

    <h3>
    MP3/WAV/MIDI → Jianpu PDF
    </h3>


    <form action="/upload"
          method="post"
          enctype="multipart/form-data">

    <input type="file"
           name="file">

    <br><br>

    <button type="submit">
    Convert
    </button>

    </form>


    </body>
    </html>
    """)



# =========================
# 執行命令工具
# =========================

def run_cmd(cmd):

    print("================")
    print("RUN:")
    print(" ".join(cmd))
    print("================")


    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )


    print(result.stdout)


    if result.returncode != 0:

        raise Exception(
            result.stdout
        )


    return result.stdout




# =========================
# 上傳
# =========================

@app.post("/upload")
async def upload(
    file: UploadFile = File(...)
):

    job_id = str(uuid.uuid4())


    work = OUTPUT_DIR / job_id

    work.mkdir()


    input_file = work / file.filename



    print("================")
    print("收到:")
    print(file.filename)
    print("================")


    # 保存檔案

    with open(
        input_file,
        "wb"
    ) as f:

        shutil.copyfileobj(
            file.file,
            f
        )


    print(
        "保存完成:",
        input_file
    )



    ext = input_file.suffix.lower()



    try:


        # -------------------------
        # MIDI
        # -------------------------

        if ext == ".mid" or ext == ".midi":


            midi = input_file



        # -------------------------
        # MP3 WAV
        # -------------------------

        elif ext in [
            ".mp3",
            ".wav"
        ]:


            print(
                "開始 BasicPitch"
            )


            midi = work / "basicpitch.mid"


            run_cmd(
                [
                    "python",
                    "basicpitch_convert.py",
                    str(input_file),
                    str(midi)
                ]
            )



        else:


            return {
                "error":
                "只支援 mp3 wav midi"
            }



        # =====================
        # MIDI → MusicXML
        # =====================


        print(
            "MIDI TO MUSICXML"
        )


        musicxml = work / "input.musicxml"


        run_cmd(
            [
                "python",
                "converter.py",
                str(midi),
                str(musicxml)
            ]
        )



        # =====================
        # 清理 MusicXML
        # =====================


        clean_xml = (
            work /
            "clean.musicxml"
        )


        print(
            "開始 MusicXML 清理"
        )


        run_cmd(
            [
                "python",
                "clean_musicxml.py",
                str(musicxml),
                str(clean_xml)
            ]
        )



        # =====================
        # jianpu_ly
        # =====================


        ly_file = (
            work /
            "jianpu.ly"
        )


        pdf_file = (
            work /
            "jianpu.pdf"
        )


        print(
            "開始 jianpu_ly"
        )


        with open(
            ly_file,
            "w",
            encoding="utf-8"
        ) as out:


            subprocess.run(
                [
                    "python",
                    "-m",
                    "jianpu_ly",
                    str(clean_xml)
                ],
                stdout=out,
                stderr=subprocess.STDOUT
            )



        print(
            "LY 完成"
        )



        # =====================
        # LilyPond
        # =====================


        print(
            "開始 LilyPond"
        )


        run_cmd(
            [
                "lilypond",
                "-o",
                str(work / "jianpu"),
                str(ly_file)
            ]
        )



        # LilyPond output:
        # jianpu.pdf


        if not pdf_file.exists():

            raise Exception(
                "PDF沒有產生"
            )



        print(
            "完成:",
            pdf_file
        )



        return FileResponse(
            pdf_file,
            media_type="application/pdf",
            filename="jianpu.pdf"
        )



    except Exception as e:


        print(
            "ERROR:",
            e
        )


        return {

            "status":
            "failed",

            "error":
            str(e)

        }




# =========================
# 測試
# =========================


@app.get("/health")
def health():

    return {

        "status":
        "JianpuTool v26 running"

    }