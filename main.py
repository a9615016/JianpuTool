from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

import shutil
import os

from converter import convert_musicxml
from midi_to_musicxml import midi_to_musicxml


app = FastAPI(
    title="Jianpu Generator"
)


# 網頁
app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


@app.get("/", response_class=HTMLResponse)
def home():

    with open(
        "static/index.html",
        encoding="utf-8"
    ) as f:
        return f.read()



# MusicXML → 簡譜 PDF
@app.post("/convert")
async def convert(
    file: UploadFile = File(...)
):

    os.makedirs(
        "uploads",
        exist_ok=True
    )


    xml_file = (
        "uploads/"
        + file.filename
    )


    with open(
        xml_file,
        "wb"
    ) as f:

        shutil.copyfileobj(
            file.file,
            f
        )


    pdf = convert_musicxml(
        xml_file
    )


    return FileResponse(
        pdf,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )



# MIDI → MusicXML → 簡譜 PDF
@app.post("/midi")
async def midi_convert(
    file: UploadFile = File(...)
):

    os.makedirs(
        "uploads",
        exist_ok=True
    )


    midi_file = (
        "uploads/"
        + file.filename
    )


    with open(
        midi_file,
        "wb"
    ) as f:

        shutil.copyfileobj(
            file.file,
            f
        )


    # MIDI → MusicXML

    musicxml = midi_to_musicxml(
        midi_file
    )


    # MusicXML → Jianpu PDF

    pdf = convert_musicxml(
        musicxml
    )


    return FileResponse(
        pdf,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )