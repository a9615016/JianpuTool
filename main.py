# main.py
# JianpuTool MP3 -> Jianpu PDF Pipeline

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse
import subprocess
import os
import shutil
import uuid


app = FastAPI()


BASE_DIR = "outputs"

os.makedirs(BASE_DIR, exist_ok=True)


@app.get("/")
def home():

    return HTMLResponse("""
    <html>
    <head>
    <title>JianpuTool</title>
    </head>

    <body>

    <h2>JianpuTool 簡譜產生器</h2>

    <p>
    MP3 → MIDI → MusicXML → Jianpu PDF
    </p>

    <form action="/upload" 
          method="post" 
          enctype="multipart/form-data">

        <input type="file" name="file"
               accept=".mp3,.wav">

        <button type="submit">
        開始轉換
        </button>

    </form>

    </body>
    </html>
    """)



@app.post("/upload")
async def upload(file: UploadFile = File(...)):


    job = str(uuid.uuid4())[:8]


    workdir = os.path.join(
        BASE_DIR,
        job
    )

    os.makedirs(
        workdir,
        exist_ok=True
    )


    # -----------------------
    # Save MP3
    # -----------------------

    mp3_path = os.path.join(
        workdir,
        file.filename
    )


    with open(mp3_path,"wb") as f:
        shutil.copyfileobj(
            file.file,
            f
        )


    print("================")
    print("收到:")
    print(mp3_path)
    print("================")


    # -----------------------
    # BasicPitch
    # -----------------------

    midi_path = os.path.join(
        workdir,
        "melody.mid"
    )


    print("開始 BasicPitch")


    subprocess.run(
        [
            "python",
            "basicpitch_convert.py",
            mp3_path,
            midi_path
        ],
        check=True
    )


    # -----------------------
    # Clean MIDI
    # -----------------------

    clean_mid = os.path.join(
        workdir,
        "melody_clean.mid"
    )


    print("開始 MIDI 清理")


    subprocess.run(
        [
            "python",
            "clean_midi.py",
            midi_path,
            clean_mid
        ],
        check=True
    )



    # -----------------------
    # MIDI -> MusicXML
    # -----------------------

    print("開始 MusicXML")


    subprocess.run(
        [
            "python",
            "midi_to_musicxml.py",
            clean_mid
        ],
        check=True
    )


    xml_path = clean_mid.replace(
        ".mid",
        ".musicxml"
    )


    # -----------------------
    # MusicXML -> Jianpu
    # -----------------------

    ly_path = os.path.join(
        workdir,
        "jianpu.ly"
    )


    pdf_path = os.path.join(
        workdir,
        "jianpu.pdf"
    )


    print("開始 jianpu_ly")


    with open(
        ly_path,
        "w",
        encoding="utf-8"
    ) as out:


        subprocess.run(
            [
                "python",
                "-m",
                "jianpu_ly",
                xml_path
            ],
            stdout=out,
            stderr=subprocess.PIPE,
            text=True
        )



    # -----------------------
    # LilyPond
    # -----------------------

    print("開始 LilyPond")


    subprocess.run(
        [
            "lilypond",
            "-o",
            os.path.join(workdir,"jianpu"),
            ly_path
        ],
        check=True
    )


    print("完成")



    return FileResponse(
        path=pdf_path,
        filename="jianpu.pdf",
        media_type="application/pdf"
    )