from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse

import os
import uuid
import subprocess
import shutil


app = FastAPI()


BASE = "/app/outputs"


os.makedirs(BASE, exist_ok=True)



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
        raise Exception(result.stdout)

    return result.stdout




@app.get("/")
def home():

    return {
        "name":"JianpuTool",
        "status":"running"
    }




@app.post("/upload")
async def upload(file: UploadFile = File(...)):


    task_id = str(uuid.uuid4())


    work = os.path.join(
        BASE,
        task_id
    )


    os.makedirs(work, exist_ok=True)


    print("====================")
    print("開始任務:",task_id)
    print("收到:",file.filename)



    mp3 = os.path.join(
        work,
        file.filename
    )


    with open(mp3,"wb") as f:

        shutil.copyfileobj(
            file.file,
            f
        )


    print("MP3保存完成")



    midi = os.path.join(
        work,
        "melody.mid"
    )


    # MP3 -> MIDI

    run([
        "python",
        "basicpitch_convert.py",
        mp3,
        midi
    ])


    print("MIDI完成")



    musicxml = os.path.join(
        work,
        "input.musicxml"
    )


    # MIDI -> MusicXML

    run([
        "python",
        "midi_to_musicxml.py",
        midi,
        musicxml
    ])


    print("MusicXML完成")



    clean = os.path.join(
        work,
        "clean.musicxml"
    )


    # MusicXML清理

    run([
        "python",
        "clean_musicxml.py",
        musicxml,
        clean
    ])


    print("清理完成")



    safe = os.path.join(
        work,
        "jianpu_safe.musicxml"
    )


    # ★ 最後 jianpu_ly 前處理

    run([
        "python",
        "jianpu_preprocess.py",
        clean,
        safe
    ])



    print("CHECK jianpu input:")
    print(safe)



    # MusicXML -> LilyPond

    ly = os.path.join(
        work,
        "output.ly"
    )


    result = subprocess.run(
        [
            "python",
            "-m",
            "jianpu_ly",
            safe
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )


    print(result.stdout)



    if result.returncode != 0:

        return JSONResponse(
            {
                "error":"jianpu_ly失敗",
                "log":result.stdout
            }
        )



    # 找 ly

    for f in os.listdir(work):

        if f.endswith(".ly"):

            ly=os.path.join(
                work,
                f
            )



    pdf = os.path.join(
        work,
        "jianpu.pdf"
    )


    # LilyPond PDF

    run([
        "lilypond",
        "-o",
        pdf.replace(".pdf",""),
        ly
    ])



    return FileResponse(
        pdf,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )