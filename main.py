from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import subprocess
import uuid
import os
import glob

app = FastAPI()


@app.get("/")
def home():
    return {
        "status": "JianpuTool running",
        "api": ["/convert"]
    }


@app.get("/status")
def status():
    return {
        "status": "ok"
    }


@app.post("/convert")
async def convert(file: UploadFile = File(...)):

    # 建立工作資料夾
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

    ly_file = os.path.join(
        work_dir,
        "input.ly"
    )


    # 儲存 MusicXML
    with open(musicxml_file, "wb") as f:
        f.write(await file.read())


    # MusicXML -> LilyPond
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
                musicxml_file
            ],
            stdout=out,
            stderr=subprocess.PIPE,
            text=True
        )


    # 檢查 ly
    if not os.path.exists(ly_file):
        return {
            "error": "ly file not created"
        }


    # LilyPond -> PDF
    subprocess.run(
        [
            "lilypond",
            "input.ly"
        ],
        cwd=work_dir,
        check=True
    )


    # 找 PDF
    pdf_files = glob.glob(
        os.path.join(
            work_dir,
            "*.pdf"
        )
    )


    if not pdf_files:

        return {
            "error": "PDF not generated",
            "files": os.listdir(work_dir)
        }


    pdf_file = pdf_files[0]


    return FileResponse(
        pdf_file,
        filename="jianpu.pdf",
        media_type="application/pdf"
    )