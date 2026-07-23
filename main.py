from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
import os
import uuid

from music21 import converter


app = FastAPI()


UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)



@app.get("/", response_class=HTMLResponse)
def home():

    return HTMLResponse("""
    <html>
    <body>

    <h1>🎵 JianpuTool MIDI → 簡譜</h1>

    <form action="/midi" method="post" enctype="multipart/form-data">

        <input type="file" name="file" accept=".mid">

        <br><br>

        <button type="submit">
            產生 MusicXML
        </button>

    </form>

    </body>
    </html>
    """)



@app.get("/status")
def status():

    return {
        "status": "JianpuTool MVP OK"
    }



@app.post("/midi")
async def midi(file: UploadFile = File(...)):

    try:

        filename = str(uuid.uuid4()) + ".mid"

        midi_path = os.path.join(
            UPLOAD_DIR,
            filename
        )


        # 儲存 MIDI
        with open(midi_path, "wb") as f:
            f.write(await file.read())


        # MIDI → MusicXML
        score = converter.parse(
            midi_path
        )


        xml_name = filename.replace(
            ".mid",
            ".musicxml"
        )


        xml_path = os.path.join(
            OUTPUT_DIR,
            xml_name
        )


        score.write(
            "musicxml",
            fp=xml_path
        )


        return {

            "status": "success",

            "musicxml": xml_name

        }


    except Exception as e:

        return {

            "error": str(e)

        }