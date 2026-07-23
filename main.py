from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse
import os
import shutil
import uuid

from converter import midi_to_pdf


app = FastAPI()


@app.get("/")
def home():

    with open("index.html", encoding="utf-8") as f:
        return HTMLResponse(f.read())



@app.get("/status")
def status():

    return {
        "status": "JianpuTool MVP OK",
        "api": [
            "/midi"
        ]
    }



@app.post("/midi")
async def midi_convert(
    file: UploadFile = File(...)
):

    work_id = str(uuid.uuid4())

    os.makedirs(
        "uploads",
        exist_ok=True
    )

    midi_file = f"uploads/{work_id}.mid"


    with open(midi_file, "wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )


    try:

        pdf = midi_to_pdf(
            midi_file
        )


        return FileResponse(
            pdf,
            media_type="application/pdf",
            filename="jianpu.pdf"
        )


    except Exception as e:

        return {
            "error": str(e)
        }