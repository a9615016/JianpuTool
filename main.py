import os
import uuid
import shutil
import subprocess

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse


app = FastAPI()


BASE_DIR = "outputs"

os.makedirs(BASE_DIR, exist_ok=True)



# 首頁

@app.get("/", response_class=HTMLResponse)
def home():

    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>JianpuTool</title>
    </head>

    <body>

    <h1>JianpuTool</h1>

    <h3>MusicXML → 簡譜 PDF</h3>


    <form action="/convert" method="post" enctype="multipart/form-data">

        <input type="file"
               name="file"
               accept=".musicxml,.xml">


        <br><br>


        <button type="submit">
            開始轉換
        </button>

    </form>


    </body>
    </html>
    """



# API 狀態

@app.get("/status")
def status():

    return {
        "status":"JianpuTool running",
        "api":[
            "/convert"
        ]
    }



# 轉換

@app.post("/convert")
async def convert(file: UploadFile = File(...)):


    job_id = str(uuid.uuid4())


    workdir = os.path.join(
        BASE_DIR,
        job_id
    )


    os.makedirs(workdir, exist_ok=True)



    # 儲存上傳檔案

    input_file = os.path.join(
        workdir,
        "input.musicxml"
    )


    with open(input_file,"wb") as f:

        shutil.copyfileobj(
            file.file,
            f
        )



    print("開始 MusicXML -> jianpu")

    print("輸入:", input_file)



    # -----------------------
    # clean MusicXML
    # -----------------------

    clean_file = os.path.join(
        workdir,
        "clean.musicxml"
    )


    print("開始 clean MusicXML")


    clean = subprocess.run(
        [
            "python",
            "clean_musicxml.py",
            input_file,
            clean_file
        ],
        capture_output=True,
        text=True
    )


    print(clean.stdout)


    if clean.stderr:

        print(clean.stderr)



    print(clean_file)



    # -----------------------
    # jianpu_ly
    # -----------------------

    ly_file = os.path.join(
        workdir,
        "jianpu.ly"
    )


    print("開始 jianpu_ly")



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
                clean_file
            ],
            stdout=f,
            stderr=subprocess.PIPE,
            text=True
        )



    print(
        "jianpu_ly:",
        result.returncode
    )



    if result.returncode != 0:

        print(result.stderr)

        return {
            "error": result.stderr
        }



    # -----------------------
    # LilyPond PDF
    # -----------------------

    print("開始 LilyPond")


    result = subprocess.run(
        [
            "lilypond",
            "-o",
            os.path.join(workdir,"jianpu"),
            ly_file
        ],
        capture_output=True,
        text=True
    )



    if result.returncode != 0:

        return {
            "error":result.stderr
        }



    pdf_file = os.path.join(
        workdir,
        "jianpu.pdf"
    )


    return FileResponse(
        pdf_file,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )