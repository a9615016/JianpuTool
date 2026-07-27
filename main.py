import os
import uuid
import shutil
import subprocess

from pathlib import Path

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse


app = FastAPI(
    title="JianpuTool v29"
)


BASE_DIR = Path("/app")

OUTPUT_DIR = BASE_DIR / "outputs"

OUTPUT_DIR.mkdir(
    exist_ok=True
)



# ==========================
# 執行命令
# ==========================

def run_cmd(cmd):

    print("====================")
    print("RUN:")
    print(" ".join(cmd))
    print("====================")


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



# ==========================
# 首頁
# ==========================

@app.get("/")
def home():

    return HTMLResponse(
"""
<html>

<head>
<title>JianpuTool v29</title>
</head>


<body>

<h1>
JianpuTool v29
</h1>

<h3>
MP3 / WAV → Jianpu PDF
</h3>


<form action="/upload"
method="post"
enctype="multipart/form-data">


<input type="file"
name="file">


<br><br>


<button>
Convert
</button>


</form>


</body>

</html>
"""
)



# ==========================
# Upload
# ==========================

@app.post("/upload")
async def upload(
    file: UploadFile = File(...)
):


    job_id = str(
        uuid.uuid4()
    )


    print("====================")
    print(
        "開始任務:",
        job_id
    )



    work = OUTPUT_DIR / job_id


    work.mkdir()



    input_file = work / file.filename



    print(
        "收到:",
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



    print(
        "MP3保存完成"
    )

    print(
        input_file
    )



    try:


        ext = input_file.suffix.lower()



        # =====================
        # MP3/WAV
        # =====================


        if ext in [
            ".mp3",
            ".wav"
        ]:


            midi = work / "melody.mid"



            run_cmd(
            [
                "python",
                "basicpitch_convert.py",
                str(input_file),
                str(midi)
            ]
            )


            print(
                "MIDI完成"
            )



        elif ext in [
            ".mid",
            ".midi"
        ]:


            midi = input_file



        else:


            return {
                "error":
                "unsupported file"
            }



        # =====================
        # MIDI CLEAN V29
        # =====================


        clean_mid = work / "clean.mid"



        run_cmd(
        [
            "python",
            "midi_cleaner.py",
            str(midi),
            str(clean_mid)
        ]
        )


        print(
            "MIDI CLEAN完成"
        )



        # =====================
        # MIDI → MusicXML
        # =====================


        musicxml = work / "input.musicxml"



        run_cmd(
        [
            "python",
            "midi_to_musicxml.py",
            str(clean_mid),
            str(musicxml)
        ]
        )



        print(
            "MusicXML完成"
        )



        # =====================
        # MusicXML CLEAN
        # =====================


        clean_xml = work / "clean.musicxml"



        run_cmd(
        [
            "python",
            "clean_musicxml.py",
            str(musicxml),
            str(clean_xml)
        ]
        )



        print(
            "清理完成"
        )



        # =====================
        # jianpu_ly
        # =====================


        ly_file = work / "jianpu.ly"



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
            "LY完成"
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



        pdf = work / "jianpu.pdf"



        if not pdf.exists():

            raise Exception(
                "PDF不存在"
            )



        print(
            "PDF完成:",
            pdf
        )



        return FileResponse(
            pdf,
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



# ==========================
# Health
# ==========================

@app.get("/health")
def health():

    return {
        "status":
        "JianpuTool v29 running"
    }