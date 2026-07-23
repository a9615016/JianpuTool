from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse
import shutil
import uuid
import os

from converter import convert_musicxml
from music21 import converter as m21converter


app = FastAPI()


@app.get("/")
def home():

    if os.path.exists("static/index.html"):
        with open("static/index.html", encoding="utf-8") as f:
            return HTMLResponse(f.read())

    return {
        "message": "JianpuTool MVP OK",
        "api": [
            "/convert",
            "/midi"
        ]
    }



# =========================
# MusicXML → 主旋律 → Jianpu PDF
# =========================
@app.post("/convert")
async def convert(file: UploadFile = File(...)):

    uid = str(uuid.uuid4())

    input_xml = f"/tmp/{uid}.musicxml"
    clean_xml = f"/tmp/{uid}_melody.musicxml"


    with open(input_xml, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )


    print("Input XML:", input_xml)


    # 讀取 MusicXML
    score = m21converter.parse(input_xml)


    # 只取第一個 part (主旋律)
    melody = score.parts[0]


    melody_score = melody.makeMeasures()


    melody_score.write(
        "musicxml",
        fp=clean_xml
    )


    print("Clean XML:", clean_xml)



    # MusicXML → Jianpu PDF
    pdf = convert_musicxml(
        clean_xml
    )


    return FileResponse(
        pdf,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )





# =========================
# MIDI → MusicXML → Jianpu
# =========================
@app.post("/midi")
async def midi_convert(file: UploadFile = File(...)):

    uid = str(uuid.uuid4())


    midi = f"/tmp/{uid}.mid"
    xml = f"/tmp/{uid}.musicxml"


    with open(midi,"wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )


    print("MIDI:", midi)


    score = m21converter.parse(
        midi
    )


    # 取主旋律
    melody = score.parts[0]


    melody.write(
        "musicxml",
        fp=xml
    )


    print("XML:", xml)



    pdf = convert_musicxml(
        xml
    )


    return FileResponse(
        pdf,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )