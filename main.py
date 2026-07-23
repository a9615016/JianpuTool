from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse
import os
import shutil
import uuid

from converter import convert_musicxml

app = FastAPI(
    title="JianpuTool",
    description="MIDI / MusicXML → Jianpu PDF",
    version="1.0"
)


@app.get("/")
def home():
    return HTMLResponse("""
    <h1>JianpuTool</h1>

    <h2>MIDI → Jianpu PDF</h2>
    <form action="/midi" method="post" enctype="multipart/form-data">
        <input type="file" name="file" accept=".mid,.midi">
        <button type="submit">Convert MIDI</button>
    </form>

    <hr>

    <h2>MusicXML → Jianpu PDF</h2>
    <form action="/musicxml" method="post" enctype="multipart/form-data">
        <input type="file" name="file" accept=".musicxml,.xml">
        <button type="submit">Convert MusicXML</button>
    </form>
    """)


# =========================
# MIDI 上傳
# =========================

@app.post("/midi")
async def midi_convert(file: UploadFile = File(...)):

    work = "/tmp"

    uid = str(uuid.uuid4())

    midi_path = os.path.join(
        work,
        uid + ".mid"
    )

    musicxml_path = os.path.join(
        work,
        uid + ".musicxml"
    )


    # 儲存 MIDI
    with open(midi_path, "wb") as f:
        shutil.copyfileobj(file.file, f)


    # MIDI → MusicXML
    from music21 import converter

    score = converter.parse(midi_path)

    score.write(
        "musicxml",
        fp=musicxml_path
    )


    # MusicXML → PDF
    pdf = convert_musicxml(
        musicxml_path
    )


    return FileResponse(
        pdf,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )



# =========================
# MusicXML 上傳
# =========================

@app.post("/musicxml")
async def musicxml_convert(file: UploadFile = File(...)):

    work = "/tmp"

    uid = str(uuid.uuid4())

    musicxml_path = os.path.join(
        work,
        uid + ".musicxml"
    )


    # 儲存 MusicXML

    with open(musicxml_path, "wb") as f:
        shutil.copyfileobj(file.file, f)


    # MusicXML → PDF

    pdf = convert_musicxml(
        musicxml_path
    )


    return FileResponse(
        pdf,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )