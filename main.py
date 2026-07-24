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
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>JianpuTool</title>
    </head>

    <body>

    <h1>JianpuTool</h1>

    <h3>MusicXML → 簡譜 PDF</h3>

    <form action="/convert"
          method="post"
          enctype="multipart/form-data">

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



@app.get("/status")
def status():

    return {
        "status":"JianpuTool running",
        "api":["/convert"]
    }




@app.post("/convert")
async def convert(file: UploadFile = File(...)):


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


    with open(input_file, "wb") as f:

        shutil.copyfileobj(
            file.file,
            f
        )



    print("開始 MusicXML -> jianpu")
    print("輸入:", input_file)



    # =====================
    # clean
    # =====================

    clean_file = os.path.join(
        workdir,
        "clean.musicxml"
    )


    print("開始 clean MusicXML")


    r = subprocess.run(
        [
            "python",
            "clean_musicxml.py",
            input_file,
            clean_file
        ],
        capture_output=True,
        text=True
    )


    print(r.stdout)


    if r.returncode != 0:

        return {
            "error": r.stderr
        }



    print(clean_file)



    # =====================
    # rebuild
    # =====================

    rebuild_file = os.path.join(
        workdir,
        "rebuild.musicxml"
    )


    print("開始 rebuild MusicXML")


    r = subprocess.run(
        [
            "python",
            "rebuild_musicxml.py",
            clean_file,
            rebuild_file
        ],
        capture_output=True,
        text=True
    )


    print(r.stdout)


    if r.returncode != 0:

        return {
            "error": r.stderr
        }



    print(rebuild_file)



    # =====================
    # jianpu_ly
    # =====================

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


        r = subprocess.run(
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
        r.returncode
    )



    if r.returncode != 0:

        print(r.stderr)

        return {
            "error": r.stderr
        }



    # =====================
    # LilyPond
    # =====================

    print("開始 LilyPond")


    print(
        "jianpu.ly exists:",
        os.path.exists(ly_file)
    )


    print(
        "LilyPond workdir:",
        os.path.abspath(workdir)
    )


    r = subprocess.run(
        [
            "lilypond",
            "-o",
            "jianpu",
            "jianpu.ly"
        ],
        cwd=os.path.abspath(workdir),
        capture_output=True,
        text=True,
        timeout=120
    )


    print(r.stdout)


    if r.stderr:

        print(r.stderr)



    if r.returncode != 0:

        return {
            "error": r.stderr
        }



    # =====================
    # PDF
    # =====================

    pdf_file = os.path.join(
        workdir,
        "jianpu.pdf"
    )


    if not os.path.exists(pdf_file):

        return {
            "error":"PDF沒有產生"
        }


    print(
        "PDF完成:",
        pdf_file
    )


    return FileResponse(
        pdf_file,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )