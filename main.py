from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import subprocess
import uuid
import os
import glob
import music21


app = FastAPI()


@app.get("/")
def home():
    return {
        "status": "JianpuTool running",
        "api": [
            "/convert",
            "/midi"
        ]
    }


@app.get("/status")
def status():
    return {
        "status": "ok"
    }



# ==========================
# 共用：MusicXML -> PDF
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


    # LilyPond PDF
    result = subprocess.run(
        [
            "lilypond",
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
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            "attachment; filename=jianpu.pdf"
        }
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


    # 儲存 MIDI

    with open(
        midi_file,
        "wb"
    ) as f:

        f.write(
            await file.read()
        )


    try:

        # MIDI -> MusicXML

        score = music21.converter.parse(
            midi_file
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



    # MusicXML -> PDF

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
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            "attachment; filename=jianpu.pdf"
        }
    )