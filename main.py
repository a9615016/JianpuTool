from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse
import subprocess
import uuid
import os
import glob
import music21


app = FastAPI()


# LilyPond
LILYPOND = r"C:\lilypond-2.26.0\bin\lilypond.exe"

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


    <h3>MusicXML → PDF</h3>

    <form action="/convert" method="post"
          enctype="multipart/form-data">

        <input type="file" name="file">

        <br><br>

        <button type="submit">
            產生簡譜 PDF
        </button>

    </form>


    <hr>


    <h3>MIDI → PDF</h3>

    <form action="/midi" method="post"
          enctype="multipart/form-data">

        <input type="file" name="file">

        <br><br>

        <button type="submit">
            MIDI 轉簡譜
        </button>

    </form>


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

    print(
        "開始 MusicXML -> jianpu",
        flush=True
    )


    clean_file = os.path.join(
        work_dir,
        "clean.musicxml"
    )


    # MusicXML 清理

    subprocess.run(
        [
            "python",
            "clean_musicxml.py",
            musicxml_file,
            clean_file
        ],
        check=True
    )


    print(
        "clean完成",
        flush=True
    )



    ly_file = os.path.join(
        work_dir,
        "input.ly"
    )


    # jianpu_ly

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
                clean_file
            ],
            stdout=out,
            stderr=subprocess.PIPE,
            text=True
        )



    print(
        "jianpu_ly:",
        result.returncode,
        flush=True
    )


    if result.returncode != 0:

        return None, result.stderr



    # LilyPond

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


    print(
        result.stdout,
        flush=True
    )


    if result.returncode != 0:

        return None, result.stdout



    pdf_files = glob.glob(
        os.path.join(
            work_dir,
            "*.pdf"
        )
    )


    print(
        "PDF:",
        pdf_files,
        flush=True
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
        pdf_file,
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


        # 修正 MIDI measure

        score.makeMeasures(
            inPlace=True
        )


        score.makeTies(
            inPlace=True
        )


        score.write(
            "musicxml",
            fp=musicxml_file
        )


    except Exception as e:

        return {
            "error":
            "MIDI convert failed",
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
        pdf_file,
        filename="jianpu.pdf",
        media_type="application/pdf"
    )