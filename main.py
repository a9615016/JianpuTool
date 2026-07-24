from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse
import subprocess
import uuid
import os
import glob
import music21


app = FastAPI()


# Windows 本機
LILYPOND = r"C:\lilypond-2.26.0\bin\lilypond.exe"

# Render / Linux
if os.name != "nt":
    LILYPOND = "lilypond"



# ==========================
# 首頁
# ==========================
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

        <h1>🎵 JianpuTool MIDI → 簡譜</h1>

        <p>上傳 MIDI 或 MusicXML</p>

        <input type="file">

        <br><br>

        <button>
            產生簡譜 PDF
        </button>

    </body>

    </html>
    """



@app.get("/status")
def status():

    return {
        "status": "JianpuTool MVP OK"
    }



# ==========================
# MusicXML -> PDF
# ==========================
def musicxml_to_pdf(musicxml_file, work_dir):

    ly_file = os.path.join(
        work_dir,
        "input.ly"
    )


    # MusicXML -> LilyPond

    with open(
        ly_file,
        "w",
        encoding="utf-8"
    ) as out:


        result = subprocess.run(
            [
                "python",
                "-m",
                "jianpu_ly",
                musicxml_file
            ],
            stdout=out,
            stderr=subprocess.PIPE,
            text=True
        )


    if result.returncode != 0:

        return None, result.stderr



    # LilyPond -> PDF

    result = subprocess.run(
        [
            LILYPOND,
            "input.ly"
        ],
        cwd=work_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )


    if result.returncode != 0:

        return None, result.stdout



    pdf_files = glob.glob(
        os.path.join(
            work_dir,
            "*.pdf"
        )
    )


    if not pdf_files:

        return None, "PDF not found"


    return pdf_files[0], None





# ==========================
# MusicXML 上傳
# ==========================
@app.post("/convert")
async def convert(
    file: UploadFile = File(...)
):

    job_id = str(uuid.uuid4())


    work_dir = os.path.join(
        "outputs",
        job_id
    )


    os.makedirs(
        work_dir,
        exist_ok=True
    )



    musicxml_file = os.path.join(
        work_dir,
        "input.musicxml"
    )



    with open(
        musicxml_file,
        "wb"
    ) as f:

        f.write(
            await file.read()
        )



    pdf_file, error = musicxml_to_pdf(
        musicxml_file,
        work_dir
    )


    if error:

        return {
            "error": error
        }



    return FileResponse(
        path=pdf_file,
        filename="jianpu.pdf",
        media_type="application/pdf"
    )





# ==========================
# MIDI 上傳
# ==========================
@app.post("/midi")
async def midi_convert(
    file: UploadFile = File(...)
):

    job_id = str(uuid.uuid4())


    work_dir = os.path.join(
        "outputs",
        job_id
    )


    os.makedirs(
        work_dir,
        exist_ok=True
    )



    midi_file = os.path.join(
        work_dir,
        "input.mid"
    )


    musicxml_file = os.path.join(
        work_dir,
        "input.musicxml"
    )



    with open(
        midi_file,
        "wb"
    ) as f:

        f.write(
            await file.read()
        )



    try:

        score = music21.converter.parse(
            midi_file
        )


        score.write(
            "musicxml",
            fp=musicxml_file
        )


    except Exception as e:

        return {
            "error": "MIDI convert failed",
            "detail": str(e)
        }




    pdf_file, error = musicxml_to_pdf(
        musicxml_file,
        work_dir
    )


    if error:

        return {
            "error": error
        }



    return FileResponse(
        path=pdf_file,
        filename="jianpu.pdf",
        media_type="application/pdf"
    )