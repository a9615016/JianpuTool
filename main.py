import os
import uuid
import shutil
import subprocess

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse


app = FastAPI()


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "outputs"
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)



@app.get("/")
async def home():

    index = os.path.join(
        BASE_DIR,
        "index.html"
    )

    if os.path.exists(index):

        with open(
            index,
            "r",
            encoding="utf-8"
        ) as f:

            return HTMLResponse(
                f.read()
            )

    return {
        "status": "JianpuTool running",
        "api": [
            "/upload",
            "/demucs"
        ]
    }




@app.post("/upload")
async def upload(
    file: UploadFile = File(...)
):

    print("===================")
    print("收到上傳:")
    print(file.filename)
    print("===================")


    job_id = str(uuid.uuid4())


    work_dir = os.path.join(
        OUTPUT_DIR,
        job_id
    )


    os.makedirs(
        work_dir,
        exist_ok=True
    )


    input_file = os.path.join(
        work_dir,
        file.filename
    )


    # 儲存 MP3
    with open(
        input_file,
        "wb"
    ) as f:

        shutil.copyfileobj(
            file.file,
            f
        )


    print("保存完成:")
    print(input_file)



    #################################################
    # Demucs
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

                "status": "error",

                "step": "demucs",

                "log": result.stdout

            }


    except Exception as e:

        return {

            "status": "error",

            "message": str(e)

        }



    print("Demucs完成")



    #################################################
    # 找 vocals.wav
    #################################################

    vocals = None


    for root, dirs, files in os.walk(work_dir):

        for name in files:

            if name == "vocals.wav":

                vocals = os.path.join(
                    root,
                    name
                )



    if vocals:

        print("找到人聲:")
        print(vocals)


    else:

        print("沒有找到 vocals.wav")



    #################################################
    # 下一步:
    #
    # vocals.wav
    #      |
    #      v
    # BasicPitch
    #      |
    #      v
    # melody.mid
    #      |
    #      v
    # MusicXML
    #      |
    #      v
    # jianpu_ly
    #      |
    #      v
    # PDF
    #################################################



    return {

        "status": "success",

        "message": "Demucs完成",

        "job_id": job_id,

        "vocals": vocals

    }





# 舊前端相容
@app.post("/demucs")
async def demucs(
    file: UploadFile = File(...)
):

    return await upload(file)