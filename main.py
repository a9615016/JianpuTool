import os
import uuid
import shutil

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse

from demucs_extract import extract_vocal


app = FastAPI()


OUTPUT_DIR = "outputs"

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


@app.get("/")
def home():

    return HTMLResponse(
"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>JianpuTool</title>
</head>

<body>

<h2>JianpuTool</h2>

<h3>MP3 → Demucs → vocals.wav</h3>

<form action="/demucs"
      method="post"
      enctype="multipart/form-data">

<input type="file"
       name="file"
       accept=".mp3">

<br><br>

<button type="submit">
開始分離
</button>

</form>

</body>
</html>
"""
    )



@app.post("/demucs")
async def demucs(
    file: UploadFile = File(...)
):

    job_id = str(uuid.uuid4())


    work_dir = os.path.join(
        OUTPUT_DIR,
        job_id
    )


    os.makedirs(
        work_dir,
        exist_ok=True
    )


    mp3_path = os.path.join(
        work_dir,
        file.filename
    )


    with open(
        mp3_path,
        "wb"
    ) as f:

        shutil.copyfileobj(
            file.file,
            f
        )


    print(
        "MP3:",
        mp3_path
    )


    vocals_path = os.path.join(
        work_dir,
        "vocals.wav"
    )


    # MP3 → vocals.wav
    extract_vocal(
        mp3_path,
        vocals_path
    )


    return {

        "status":
        "Demucs success",

        "mp3":
        mp3_path,

        "vocals":
        vocals_path

    }