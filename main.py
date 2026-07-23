from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import shutil
import uuid
import os

from converter import convert_musicxml


print("MAIN VERSION MVP HTML")


app = FastAPI()


# 首頁顯示 HTML
@app.get("/")
def home():

    return FileResponse(
        "index.html"
    )



# 測試
@app.get("/test")
def test():

    return {
        "message": "JianpuTool MVP OK"
    }



# =========================
# MusicXML → Jianpu PDF
# =========================

@app.post("/convert")
async def convert(
    file: UploadFile = File(...)
):

    uid = str(uuid.uuid4())


    xml_file = f"/tmp/{uid}.musicxml"


    with open(xml_file, "wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )


    print("MusicXML:", xml_file)



    pdf_path = convert_musicxml(
        xml_file
    )


    print("PDF:", pdf_path)



    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )



# =========================
# MIDI → MusicXML → Jianpu
# =========================

@app.post("/midi")
async def midi_convert(
    file: UploadFile = File(...)
):

    uid = str(uuid.uuid4())


    midi_file = f"/tmp/{uid}.mid"

    xml_file = f"/tmp/{uid}.musicxml"



    with open(midi_file, "wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )


    print("MIDI:", midi_file)



    from music21 import converter


    score = converter.parse(
        midi_file
    )


    score.write(
        "musicxml",
        fp=xml_file
    )


    print("MusicXML:", xml_file)



    pdf_path = convert_musicxml(
        xml_file
    )


    print("PDF:", pdf_path)



    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )