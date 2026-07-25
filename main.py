from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
import os
import uuid
import shutil


app = FastAPI()


OUTPUT_DIR = "outputs"

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


@app.get("/")
def home():

    if os.path.exists("index.html"):

        with open(
            "index.html",
            encoding="utf-8"
        ) as f:
            return HTMLResponse(f.read())

    return {
        "status": "JianpuTool running"
    }



@app.post("/upload")
async def upload(
    file: UploadFile = File(...)
):

    print("===================")
    print("收到上傳:")
    print(file.filename)
    print("===================")


    uid = str(uuid.uuid4())


    save_path = os.path.join(
        OUTPUT_DIR,
        uid + "_" + file.filename
    )


    with open(
        save_path,
        "wb"
    ) as f:

        shutil.copyfileobj(
            file.file,
            f
        )


    print("保存完成:")
    print(save_path)


    return {

        "status": "upload ok",

        "file": save_path

    }