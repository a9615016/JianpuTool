from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
import os
import uuid

from music21 import converter


app = FastAPI()


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")


os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


# =========================
# 首頁
# =========================

@app.get("/", response_class=HTMLResponse)
def home():

    index_path = os.path.join(
        BASE_DIR,
        "static",
        "index.html"
    )

    with open(index_path, encoding="utf-8") as f:
        return f.read()



# =========================
# 狀態測試
# =========================

@app.get("/status")
def status():

    return {
        "status": "JianpuTool running",
        "api": [
            "/midi",
            "/convert"
        ]
    }



# =========================
# MIDI -> MusicXML
# =========================

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


        # music21 讀取 MIDI
        score = converter.parse(
            midi_path
        )


        # 輸出 MusicXML
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

            "midi": filename,

            "musicxml": xml_name

        }


    except Exception as e:

        return {

            "error": str(e)

        }



# =========================
# 預留 MP3 / 其他轉換
# =========================

@app.post("/convert")
async def convert(file: UploadFile = File(...)):


    return {

        "status": "convert api ready",

        "filename": file.filename

    }