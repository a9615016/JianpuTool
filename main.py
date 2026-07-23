from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

import shutil
import uuid
import os
import tempfile


from converter import convert_musicxml


print("MAIN VERSION MVP WEB")


app = FastAPI()


# static 網頁
app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)



# 首頁
@app.get("/", response_class=HTMLResponse)
def home():

    with open(
        "static/index.html",
        "r",
        encoding="utf-8"
    ) as f:
        return f.read()



@app.get("/test")
def test():

    return {
        "message": "JianpuTool MVP OK"
    }



# ==========================
# MusicXML → Jianpu PDF
# ==========================

@app.post("/convert")
async def convert(
    file: UploadFile = File(...)
):

    uid = str(uuid.uuid4())


    xml_path = (
        f"/tmp/{uid}.musicxml"
    )


    with open(
        xml_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )


    print(
        "MusicXML:",
        xml_path
    )


    pdf_path = convert_musicxml(
        xml_path
    )


    print(
        "PDF:",
        pdf_path
    )


    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )



# ==========================
# MIDI → MusicXML → PDF
# ==========================

@app.post("/midi")
async def midi_convert(
    file: UploadFile = File(...)
):

    uid = str(uuid.uuid4())


    midi_path = (
        f"/tmp/{uid}.mid"
    )

    xml_path = (
        f"/tmp/{uid}.musicxml"
    )


    with open(
        midi_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )


    print(
        "MIDI:",
        midi_path
    )


    # MIDI → MusicXML

    from music21 import converter


    score = converter.parse(
        midi_path
    )


    score.write(
        "musicxml",
        fp=xml_path
    )


    print(
        "MusicXML:",
        xml_path
    )



    # MusicXML → PDF

    pdf_path = convert_musicxml(
        xml_path
    )


    print(
        "PDF:",
        pdf_path
    )


    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )