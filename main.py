from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
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





@app.get("/")
def home():

    return {
        "status":"JianpuTool",
        "pipeline":
        "MP3 -> BasicPitch -> MIDI -> Jianpu LY -> PDF"
    }





@app.post("/upload")
async def upload(
    file: UploadFile = File(...)
):

    job = str(uuid.uuid4())

    folder = os.path.join(
        BASE,
        job
    )

    os.makedirs(folder)


    mp3 = os.path.join(
        folder,
        file.filename
    )


    with open(mp3,"wb") as f:
        shutil.copyfileobj(
            file.file,
            f
        )


    print("====================")
    print("開始任務:",job)
    print("收到:",file.filename)


    #
    # 1. MP3 -> MIDI
    #

    midi = os.path.join(
        folder,
        "melody.mid"
    )


    run([
        "python",
        "basicpitch_convert.py",
        mp3,
        midi
    ])


    print("MIDI完成")



    #
    # 2. MIDI -> Jianpu Lilypond
    #

    ly = os.path.join(
        folder,
        "melody.ly"
    )


    run([
        "python",
        "midi_to_jianpu_ly.py",
        midi,
        ly
    ])



    print("LY完成")



    #
    # 3. LilyPond -> PDF
    #

    run([
        "lilypond",
        "-o",
        folder,
        ly
    ])



    pdf = os.path.join(
        folder,
        "melody.pdf"
    )


    if not os.path.exists(pdf):

        raise Exception(
            "PDF產生失敗"
        )



    print("PDF完成")



    return FileResponse(
        pdf,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )