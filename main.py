# main.py
# JianpuTool Web API

import os
import uuid
import subprocess

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse


app = FastAPI()


BASE = "/app/outputs"


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



@app.get("/")
def home():

    return """
    <h1>JianpuTool 簡譜產生器</h1>

    <form action="/upload"
          method="post"
          enctype="multipart/form-data">

    <input type="file"
           name="file">

    <button>
    Upload
    </button>

    </form>
    """



@app.post("/upload")
async def upload(file: UploadFile = File(...)):


    task_id = str(uuid.uuid4())

    task_dir = os.path.join(
        BASE,
        task_id
    )

    os.makedirs(
        task_dir,
        exist_ok=True
    )


    mp3 = os.path.join(
        task_dir,
        file.filename
    )


    with open(mp3,"wb") as f:
        f.write(
            await file.read()
        )


    print("====================")
    print("開始任務:",task_id)
    print("收到:",file.filename)


    # =====================
    # MP3 -> MIDI
    # =====================

    midi = os.path.join(
        task_dir,
        "melody.mid"
    )


    run([
        "python",
        "basicpitch_convert.py",
        mp3,
        midi
    ])


    print("MIDI完成")


    # =====================
    # MIDI -> MusicXML
    # =====================

    musicxml = os.path.join(
        task_dir,
        "input.musicxml"
    )


    run([
        "python",
        "midi_to_musicxml.py",
        midi,
        musicxml
    ])


    print("MusicXML完成")



    # =====================
    # clean
    # =====================

    clean = os.path.join(
        task_dir,
        "clean.musicxml"
    )


    run([
        "python",
        "clean_musicxml.py",
        musicxml,
        clean
    ])


    print("清理完成")



    # =====================
    # jianpu fix
    # =====================

    fixed = os.path.join(
        task_dir,
        "fixed.musicxml"
    )


    run([
        "python",
        "jianpu_fix_musicxml.py",
        clean,
        fixed
    ])


    print("jianpu修正完成")



    # =====================
    # MusicXML -> LY
    # =====================

    run([
        "python",
        "-m",
        "jianpu_ly",
        fixed
    ])


    ly = os.path.join(
        task_dir,
        "fixed.ly"
    )


    # 找 jianpu_ly 產生的 ly
    for f in os.listdir(task_dir):

        if f.endswith(".ly"):

            ly = os.path.join(
                task_dir,
                f
            )



    # =====================
    # LY -> PDF
    # =====================

    run([
        "lilypond",
        "--pdf",
        ly
    ])


    pdf = ly.replace(
        ".ly",
        ".pdf"
    )


    print("PDF完成")
    print(pdf)



    return FileResponse(
        pdf,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )