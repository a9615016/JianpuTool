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



# =====================
# 首頁
# =====================

@app.get("/", response_class=HTMLResponse)
def home():

    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>JianpuTool</title>
    </head>

    <body>

    <h1>🎵 JianpuTool MIDI → 簡譜</h1>

    <form action="/midi" method="post" enctype="multipart/form-data">

        <input 
            type="file" 
            name="file"
            accept=".mid,.midi"
        >

        <br><br>

        <button type="submit">
            產生 MusicXML
        </button>

    </form>

    </body>
    </html>
    """)



# =====================
# 狀態
# =====================

@app.get("/status")
def status():

    return {
        "status": "JianpuTool running",
        "api": [
            "/midi"
        ]
    }



# =====================
# MIDI → MusicXML
# =====================

@app.post("/midi")
async def midi(file: UploadFile = File(...)):

    try:

        # 建立唯一檔名
        midi_name = (
            str(uuid.uuid4())
            + ".mid"
        )


        midi_path = os.path.join(
            UPLOAD_DIR,
            midi_name
        )


        # 儲存 MIDI
        with open(midi_path, "wb") as f:

            content = await file.read()

            f.write(content)



        # music21 讀 MIDI

        score = converter.parse(
            midi_path
        )



        # 輸出 MusicXML

        xml_name = midi_name.replace(
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

            "midi": midi_name,

            "musicxml": xml_name

        }



    except Exception as e:

        return {

            "status": "failed",

            "error": str(e)

        }