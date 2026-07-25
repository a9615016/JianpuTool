import os
import uuid
import subprocess

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse


app = FastAPI()


BASE_DIR = "/app"


def run_command(cmd):

    print("執行:", " ".join(cmd))

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

    with open("index.html", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.post("/convert")
async def convert(file: UploadFile = File(...)):


    job = str(uuid.uuid4())

    work = os.path.join(
        "outputs",
        job
    )

    os.makedirs(work, exist_ok=True)


    # 1. 儲存 MP3

    mp3 = os.path.join(
        work,
        file.filename
    )

    with open(mp3,"wb") as f:
        f.write(await file.read())


    print("MP3:", mp3)



    # 2. Demucs 分離 vocals

    vocals = os.path.join(
        work,
        "vocals.wav"
    )


    run_command([
        "python",
        "demucs_extract.py",
        mp3,
        vocals
    ])



    # 3. BasicPitch 產生 MIDI

    midi = os.path.join(
        work,
        "melody.mid"
    )


    run_command([
        "python",
        "basicpitch_extract.py",
        vocals,
        midi
    ])



    # 4. MIDI → MusicXML

    musicxml = os.path.join(
        work,
        "score.musicxml"
    )


    run_command([
        "python",
        "midi_to_musicxml.py",
        midi,
        musicxml
    ])



    # 5. MusicXML 清理

    clean_xml = os.path.join(
        work,
        "clean.musicxml"
    )


    run_command([
        "python",
        "clean_musicxml.py",
        musicxml,
        clean_xml
    ])



    # 6. Jianpu

    ly = os.path.join(
        work,
        "jianpu.ly"
    )


    with open(ly,"w",encoding="utf-8") as f:

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



    # 7. LilyPond PDF

    run_command([
        "lilypond",
        "-o",
        os.path.join(work,"jianpu"),
        ly
    ])



    pdf = os.path.join(
        work,
        "jianpu.pdf"
    )


    return FileResponse(
        pdf,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )