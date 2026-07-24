import os
import subprocess
import uuid
import shutil

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse


app = FastAPI()


BASE_DIR = "outputs"

os.makedirs(BASE_DIR, exist_ok=True)



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


    job_id = str(uuid.uuid4())

    workdir = os.path.join(
        BASE_DIR,
        job_id
    )

    os.makedirs(workdir, exist_ok=True)



    # 上傳檔案

    input_file = os.path.join(
        workdir,
        file.filename
    )


    with open(input_file,"wb") as f:

        shutil.copyfileobj(
            file.file,
            f
        )



    print("開始 MusicXML -> jianpu")

    print("輸入:", input_file)



    #
    # 1. clean MusicXML
    #

    clean_file = os.path.join(
        workdir,
        "clean.musicxml"
    )



    print("開始 clean MusicXML")


    result = subprocess.run(
        [
            "python",
            "clean_musicxml.py",
            input_file,
            clean_file
        ],
        capture_output=True,
        text=True
    )


    print(result.stdout)

    if result.stderr:

        print(result.stderr)



    print(clean_file)



    #
    # 2. jianpu_ly
    #

    ly_file = os.path.join(
        workdir,
        "jianpu.ly"
    )


    print("開始 jianpu_ly")



    with open(ly_file,"w",encoding="utf-8") as f:


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




    #
    # 3. LilyPond PDF
    #

    pdf_file = os.path.join(
        workdir,
        "jianpu.pdf"
    )


    print("開始 LilyPond")



    result = subprocess.run(
        [
            "lilypond",
            "-o",
            pdf_file.replace(".pdf",""),
            ly_file
        ],
        capture_output=True,
        text=True
    )



    if result.returncode !=0:

        return {
            "error": result.stderr
        }



    return FileResponse(
        pdf_file,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )