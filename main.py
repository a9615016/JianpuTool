from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import subprocess
import uuid
import os

app = FastAPI()

LILYPOND = r"C:\lilypond-2.26.0\bin\lilypond.exe"


@app.get("/")
def home():
    return {
        "status": "JianpuTool running",
        "api": [
            "/convert"
        ]
    }


@app.post("/convert")
async def convert(file: UploadFile = File(...)):

    work = str(uuid.uuid4())

    os.makedirs(work, exist_ok=True)

    musicxml = f"{work}/input.musicxml"
    ly = f"{work}/input.ly"
    pdf = f"{work}/input.pdf"


    # 儲存 MusicXML
    with open(musicxml, "wb") as f:
        f.write(await file.read())


    # MusicXML -> LilyPond
    with open(ly, "w", encoding="utf-8") as out:
        subprocess.run(
            [
                "python",
                "-m",
                "jianpu_ly",
                musicxml
            ],
            stdout=out,
            check=True
        )


    # LilyPond -> PDF
    subprocess.run(
        [
            LILYPOND,
            ly
        ],
        cwd=work,
        check=True
    )


    return FileResponse(
        pdf,
        filename="jianpu.pdf"
    )