from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import shutil
import uuid
import traceback

from converter import convert_musicxml


print("MAIN VERSION FINAL")


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


@app.get("/test")
def test():
    return {
        "message": "new main.py"
    }



# MusicXML → Jianpu PDF
@app.post("/convert")
async def convert(file: UploadFile = File(...)):

    try:

        uid = str(uuid.uuid4())

        musicxml_path = f"/tmp/{uid}.musicxml"


        with open(musicxml_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)


        print("MusicXML:", musicxml_path)


        pdf_path = convert_musicxml(
            musicxml_path
        )


        print("PDF:", pdf_path)


        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename="jianpu.pdf"
        )


    except Exception:

        traceback.print_exc()

        return {
            "error": "convert failed"
        }





# MIDI → MusicXML → Jianpu PDF
@app.post("/midi")
async def midi_convert(file: UploadFile = File(...)):

    try:

        uid = str(uuid.uuid4())

        midi_path = f"/tmp/{uid}.mid"
        musicxml_path = f"/tmp/{uid}.musicxml"


        with open(midi_path, "wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer
            )


        print("MIDI:", midi_path)


        from music21 import converter


        score = converter.parse(
            midi_path
        )


        print("music21 OK")


        score.write(
            "musicxml",
            fp=musicxml_path
        )


        print("MusicXML:", musicxml_path)



        pdf_path = convert_musicxml(
            musicxml_path
        )


        print("PDF:", pdf_path)



        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename="jianpu.pdf"
        )


    except Exception:

        traceback.print_exc()

        return {
            "error": "midi convert failed"
        }