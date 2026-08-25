"""
main.py (FastAPI 版本主頁)

如果你的專案是以 streamlit_app.py 當主頁，這支 main.py 是「備用/API 版」，
兩者共用同一份 pipeline.py，邏輯不會分岔。不需要 FastAPI 介面的話，
這支檔案可以不用啟動。

用法:
    uvicorn main:app --reload
    或
    python main.py song.mp3   (命令列直接測試，不開網頁伺服器)
"""

import os
import sys
import uuid

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse

from pipeline import convert_pipeline, OUTPUT_DIR


app = FastAPI(title="JianpuTool")


@app.get("/")
def home():

    return HTMLResponse("""
    <html>
    <body>
    <h2>JianpuTool</h2>
    <form action="/upload" method="post" enctype="multipart/form-data">
    <input type="file" name="file">
    <button type="submit">Convert</button>
    </form>
    </body>
    </html>
    """)


@app.post("/upload")
async def upload(file: UploadFile = File(...)):

    job = str(uuid.uuid4())
    workdir = os.path.join(OUTPUT_DIR, job)
    os.makedirs(workdir, exist_ok=True)

    input_audio = os.path.join(workdir, file.filename)

    with open(input_audio, "wb") as f:
        f.write(await file.read())

    print("INPUT:", input_audio)

    pdf = convert_pipeline(input_audio, workdir)

    return FileResponse(pdf, media_type="application/pdf", filename="jianpu.pdf")


if __name__ == "__main__":

    # 命令列測試用法: python main.py song.mp3
    if len(sys.argv) < 2:
        print("用法: python main.py input.mp3")
        sys.exit(1)

    input_audio = sys.argv[1]
    job = str(uuid.uuid4())
    workdir = os.path.join(OUTPUT_DIR, job)
    os.makedirs(workdir, exist_ok=True)

    pdf = convert_pipeline(input_audio, workdir)

    print("\n完成 PDF:", pdf)
