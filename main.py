import os
import uuid
import shutil
import subprocess

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse


app = FastAPI()


BASE_DIR = "outputs"

os.makedirs(BASE_DIR, exist_ok=True)



@app.get("/", response_class=HTMLResponse)
def home():

    return """
    <html>
    <head>
        <meta charset="utf-8">
        <title>JianpuTool</title>
    </head>

    <body>

    <h1>JianpuTool</h1>

    <h3>MUSICXML → 簡譜 PDF</h3>


    <form action="/convert"
          method="post"
          enctype="multipart/form-data">

        <input type="file"
               name="file"
               accept=".musicxml,.xml">

        <br><br>

        <button>
        轉換簡譜
        </button>

    </form>


    </body>
    </html>
    """



@app.get("/status")
def status():

    return {
        "status":"JianpuTool running",
        "api":[
            "/convert"
        ]
    }



@app.post("/convert")
async def convert(
    file: UploadFile = File(...)
):


    job_id = str(uuid.uuid4())


    workdir = os.path.join(
        BASE_DIR,
        job_id
    )


    os.makedirs(
        workdir,
        exist_ok=True
    )


    input_file = os.path.join(
        workdir,
        "input.musicxml"
    )


    with open(
        input_file,
        "wb"
    ) as f:

        shutil.copyfileobj(
            file.file,
            f
        )



    print("開始 MusicXML -> Jianpu")



    # -------------------
    # clean
    # -------------------

    clean_file = os.path.join(
        workdir,
        "clean.musicxml"
    )


    subprocess.run(
        [
            "python",
            "clean_musicxml.py",
            input_file,
            clean_file
        ]
    )



    print(clean_file)



    # -------------------
    # rebuild
    # -------------------

    rebuild_file = os.path.join(
        workdir,
        "rebuild.musicxml"
    )


    subprocess.run(
        [
            "python",
            "rebuild_musicxml.py",
            clean_file,
            rebuild_file
        ]
    )


    print(rebuild_file)



    # -------------------
    # jianpu_ly
    # -------------------

    ly_file = os.path.join(
        workdir,
        "jianpu.ly"
    )



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
                rebuild_file
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

        return {
            "error":result.stderr
        }



    # -------------------
    # LilyPond
    # -------------------


    result = subprocess.run(
        [
            "lilypond",
            "-o",
            "jianpu",
            "jianpu.ly"
        ],
        cwd=workdir,
        capture_output=True,
        text=True
    )



    print(result.stdout)
    print(result.stderr)



    pdf_file=os.path.join(
        workdir,
        "jianpu.pdf"
    )



    if not os.path.exists(pdf_file):

        return {
            "error":"PDF產生失敗"
        }



    return FileResponse(
        pdf_file,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )