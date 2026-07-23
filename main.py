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


    # 儲存上傳 MusicXML
    with open(
        musicxml_file,
        "wb"
    ) as f:
        f.write(await file.read())


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
        return {
            "error": "jianpu_ly failed",
            "detail": result.stderr
        }


    # 確認 ly
    if not os.path.exists(ly_file):
        return {
            "error": "input.ly not created"
        }


    # LilyPond -> PDF
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
        return {
            "error": "lilypond failed",
            "detail": result.stdout
        }


    # 搜尋 PDF
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


    print("下載 PDF:", pdf_file)
    print("PDF存在:", os.path.exists(pdf_file))


    # 強制下載
    return FileResponse(
        path=pdf_file,
        filename="jianpu.pdf",
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            "attachment; filename=jianpu.pdf"
        }
    )