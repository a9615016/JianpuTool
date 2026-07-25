import os
import uuid
import shutil
import subprocess

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse


app = FastAPI()


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

os.makedirs(OUTPUT_DIR, exist_ok=True)



@app.get("/")
async def home():

    html_path = os.path.join(BASE_DIR, "index.html")

    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())

    return {
        "status": "JianpuTool running",
        "api": [
            "/upload",
            "/demucs"
        ]
    }



@app.post("/upload")
async def upload(file: UploadFile = File(...)):

    job_id = str(uuid.uuid4())

    work_dir = os.path.join(
        OUTPUT_DIR,
        job_id
    )

    os.makedirs(work_dir, exist_ok=True)


    input_file = os.path.join(
        work_dir,
        file.filename
    )


    # 儲存上傳 MP3
    with open(input_file, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )


    print("收到檔案:")
    print(input_file)


    #################################################
    # 1. Demucs 分離人聲
    #################################################

    print("開始 Demucs")


    try:

        result = subprocess.run(
            [
                "python",
                "-m",
                "demucs",
                input_file,
                "-o",
                work_dir
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )


        print(result.stdout)


        if result.returncode != 0:

            return {
                "error": "Demucs failed",
                "log": result.stdout
            }


    except Exception as e:

        return {
            "error": str(e)
        }



    #################################################
    # 2. 後續接 MIDI / MusicXML / Jianpu
    #################################################

    print("Demucs完成")



    return {

        "status": "success",

        "message": "音訊分離完成",

        "job_id": job_id,

        "folder": work_dir

    }





# 相容舊版 index.html
@app.post("/demucs")
async def demucs(file: UploadFile = File(...)):

    return await upload(file)