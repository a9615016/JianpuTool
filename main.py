from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse
import shutil
import uuid
import os

from converter import convert_musicxml


print("MAIN VERSION MIDI + MUSICXML CLEAN")

app = FastAPI()


@app.get("/")
def home():

    if os.path.exists("static/index.html"):
        with open(
            "static/index.html",
            "r",
            encoding="utf-8"
        ) as f:
            return HTMLResponse(f.read())

    return {
        "message": "JianpuTool MVP OK",
        "api": [
            "/convert",
            "/midi"
        ]
    }



@app.get("/test")
def test():
    return {
        "message": "server ok"
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


    with open(xml_file,"wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )


    print(
        "MusicXML:",
        xml_file
    )


    try:

        pdf = convert_musicxml(
            xml_file
        )


    except Exception as e:

        return {
            "error": str(e)
        }


    return FileResponse(
        pdf,
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


    with open(midi_file,"wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )


    print(
        "MIDI:",
        midi_file
    )


    try:

        from music21 import converter


        score = converter.parse(
            midi_file
        )


        # 只保留第一個旋律 Part
        if len(score.parts) > 1:
            score = score.parts[0]


        score.write(
            "musicxml",
            fp=xml_file
        )


        print(
            "MusicXML:",
            xml_file
        )


        pdf = convert_musicxml(
            xml_file
        )


    except Exception as e:

        return {
            "error": str(e)
        }



    return FileResponse(
        pdf,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )