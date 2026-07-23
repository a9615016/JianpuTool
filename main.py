from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import shutil
import os
import uuid

from converter import convert_musicxml


app = FastAPI()


@app.get("/")
def home():
    return {
        "status": "JianpuTool running",
        "api": [
            "/convert",
            "/midi"
        ]
    }



# MusicXML → PDF
@app.post("/convert")
async def convert(file: UploadFile = File(...)):

    uid = str(uuid.uuid4())

    musicxml_path = f"/tmp/{uid}.musicxml"
    pdf_path = f"/tmp/{uid}.pdf"


    with open(musicxml_path, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )


    result = convert_musicxml(
        musicxml_path,
        pdf_path
    )


    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )



# MIDI → PDF
@app.post("/midi")
async def midi_convert(file: UploadFile = File(...)):

    uid = str(uuid.uuid4())

    midi_path = f"/tmp/{uid}.mid"
    musicxml_path = f"/tmp/{uid}.musicxml"
    pdf_path = f"/tmp/{uid}.pdf"


    with open(midi_path,"wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )


    # MIDI → MusicXML
    from music21 import converter

    score = converter.parse(midi_path)

    score.write(
        "musicxml",
        fp=musicxml_path
    )


    print("MIDI:", midi_path)
    print("MusicXML:", musicxml_path)


    convert_musicxml(
        musicxml_path,
        pdf_path
    )


    print("PDF:", pdf_path)


    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )