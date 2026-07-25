from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
import os
import uuid
import shutil

from demucs_extract import extract_vocal


app = FastAPI()


OUTPUT_DIR = "outputs"

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# 首頁
@app.get("/")
def home():

    if os.path.exists("index.html"):

        with open(
            "index.html",
            encoding="utf-8"
        ) as f:

            return HTMLResponse(
                f.read()
            )

    return {
        "status": "JianpuTool running"
    }



# 上傳 MP3
@app.post("/upload")
async def upload(
    file: UploadFile = File(...)
):

    print("===================")
    print("收到上傳:")
    print(file.filename)
    print("===================")


    uid = str(uuid.uuid4())


    # MP3 儲存位置
    mp3_path = os.path.join(
        OUTPUT_DIR,
        uid + "_" + file.filename
    )


    with open(
        mp3_path,
        "wb"
    ) as f:

        shutil.copyfileobj(
            file.file,
            f
        )


    print("保存完成:")
    print(mp3_path)



    # vocals 輸出
    vocals_path = os.path.join(
        OUTPUT_DIR,
        uid + "_vocals.wav"
    )


    print("開始 Demucs")


    try:

        extract_vocal(
            mp3_path,
            vocals_path
        )


    except Exception as e:

        print("Demucs 失敗:")
        print(e)

        return {

            "status":"demucs failed",

            "error":str(e)

        }



    print("vocals完成:")
    print(vocals_path)



    return {

        "status":"success",

        "mp3":mp3_path,

        "vocals":vocals_path

    }