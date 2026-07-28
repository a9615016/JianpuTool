# main.py
# JianpuTool V31
# MP3 -> BasicPitch -> Clean MIDI -> MusicXML -> Jianpu PDF

import os
import uuid
import subprocess

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse


app = FastAPI()


BASE_DIR = "/app"

OUTPUT_DIR = "/app/outputs"


os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)



@app.get("/")
def home():

    return HTMLResponse("""
    <html>
    <head>
    <title>JianpuTool</title>
    </head>

    <body>

    <h2>
    JianpuTool
    </h2>

    <p>
    MP3 → 簡譜 PDF
    </p>


    <form action="/upload"
    method="post"
    enctype="multipart/form-data">

    <input type="file"
    name="file"
    accept=".mp3,.wav">

    <br><br>

    <button type="submit">
    Convert
    </button>

    </form>


    </body>
    </html>
    """)



def run(cmd):

    print("RUN:", " ".join(cmd))

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )


    print(result.stdout)


    if result.returncode != 0:

        raise Exception(
            result.stdout
        )


    return result.stdout




@app.post("/upload")
async def upload(
    file: UploadFile = File(...)
):


    task_id = str(uuid.uuid4())


    workdir = os.path.join(
        OUTPUT_DIR,
        task_id
    )


    os.makedirs(
        workdir,
        exist_ok=True
    )


    print("====================")
    print("開始任務:", task_id)
    print("收到:", file.filename)


    # -----------------
    # save mp3
    # -----------------

    mp3 = os.path.join(
        workdir,
        file.filename
    )


    with open(mp3,"wb") as f:

        f.write(
            await file.read()
        )


    print("MP3保存完成")
    print(mp3)



    # -----------------
    # BasicPitch
    # -----------------

    melody_mid = os.path.join(
        workdir,
        "melody.mid"
    )


    run([
        "python",
        "basicpitch_convert.py",
        mp3,
        melody_mid
    ])


    print("MIDI完成")



    # -----------------
    # clean MIDI
    # -----------------

    clean_mid = os.path.join(
        workdir,
        "clean.mid"
    )


    run([
        "python",
        "clean_midi.py",
        melody_mid,
        clean_mid
    ])


    print("MIDI CLEAN完成")



    # -----------------
    # MIDI -> MusicXML
    # -----------------

    musicxml = os.path.join(
        workdir,
        "input.musicxml"
    )


    run([
        "python",
        "midi_to_musicxml.py",
        clean_mid,
        musicxml
    ])


    print("MusicXML完成")



    # -----------------
    # Clean MusicXML
    # -----------------

    clean_xml=os.path.join(
        workdir,
        "clean.musicxml"
    )


    run([
        "python",
        "clean_musicxml.py",
        musicxml,
        clean_xml
    ])


    print("清理完成")



    # -----------------
    # jianpu_ly
    # -----------------

    ly=os.path.join(
        workdir,
        "jianpu.ly"
    )


    print("開始 jianpu_ly")


    with open(
        ly,
        "w",
        encoding="utf-8"
    ) as f:


        subprocess.run(
            [
                "python",
                "-m",
                "jianpu_ly",
                clean_xml
            ],
            stdout=f,
            stderr=subprocess.STDOUT
        )



    print("LY完成")



    # -----------------
    # LilyPond
    # -----------------

    run([
        "lilypond",
        "-o",
        os.path.join(workdir,"jianpu"),
        ly
    ])



    pdf=os.path.join(
        workdir,
        "jianpu.pdf"
    )


    if not os.path.exists(pdf):

        raise Exception(
            "PDF產生失敗"
        )



    print("SUCCESS")



    return FileResponse(
        pdf,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )