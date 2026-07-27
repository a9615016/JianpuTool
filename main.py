import os
import uuid
import subprocess

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse


app = FastAPI()


@app.get("/")
def home():
    return {
        "status": "JianpuTool running",
        "version": "V26",
        "api": [
            "/upload"
        ]
    }


@app.post("/upload")
async def upload(file: UploadFile = File(...)):

    job = str(uuid.uuid4())

    work_dir = f"outputs/{job}"
    os.makedirs(work_dir, exist_ok=True)


    print("====================")
    print("開始任務:", job)
    print("收到:", file.filename)


    mp3 = os.path.join(
        work_dir,
        file.filename
    )


    with open(mp3,"wb") as f:
        f.write(await file.read())


    print("MP3保存完成")


    midi = os.path.join(
        work_dir,
        "melody.mid"
    )


    # MP3 -> MIDI
    run(
        [
            "python",
            "basicpitch_convert.py",
            mp3,
            midi
        ]
    )


    musicxml = os.path.join(
        work_dir,
        "input.musicxml"
    )


    # MIDI -> MusicXML
    run(
        [
            "python",
            "midi_to_musicxml.py",
            midi,
            musicxml
        ]
    )


    clean = os.path.join(
        work_dir,
        "clean.musicxml"
    )


    # Clean
    run(
        [
            "python",
            "clean_musicxml.py",
            musicxml,
            clean
        ]
    )


    fixed = os.path.join(
        work_dir,
        "jianpu_fixed.musicxml"
    )


    # V26 FIX
    run(
        [
            "python",
            "jianpu_fix_musicxml.py",
            clean,
            fixed
        ]
    )


    ly = os.path.join(
        work_dir,
        "output.ly"
    )


    # jianpu_ly
    result=subprocess.run(
        [
            "python",
            "-m",
            "jianpu_ly",
            fixed
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )


    print(result.stdout)


    if result.returncode !=0:
        return {
            "error": result.stdout
        }



    pdf = os.path.join(
        work_dir,
        "output.pdf"
    )


    # Lilypond
    run(
        [
            "lilypond",
            "-o",
            pdf.replace(".pdf",""),
            ly
        ]
    )


    return FileResponse(
        pdf,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )



def run(cmd):

    print("RUN:",
          " ".join(cmd))

    result=subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    print(result.stdout)


    if result.returncode!=0:

        raise Exception(
            result.stdout
        )