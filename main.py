from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import os
import uuid
import subprocess


app = FastAPI()


BASE = "/app/outputs"


os.makedirs(
    BASE,
    exist_ok=True
)



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



@app.post("/upload")
async def upload(
    file: UploadFile = File(...)
):

    job = str(uuid.uuid4())

    folder = os.path.join(
        BASE,
        job
    )


    os.makedirs(
        folder,
        exist_ok=True
    )


    print("====================")
    print("開始任務:", job)
    print("收到:", file.filename)



    # =====================
    # save mp3
    # =====================

    mp3 = os.path.join(
        folder,
        file.filename
    )


    with open(mp3,"wb") as f:

        f.write(
            await file.read()
        )


    print("MP3保存完成")



    # =====================
    # MP3 -> MIDI
    # =====================

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



    # =====================
    # MIDI QUANTIZE ⭐
    # =====================

    qmid = os.path.join(
        folder,
        "quantized.mid"
    )


    run([
        "python",
        "midi_quantize.py",
        midi,
        qmid
    ])


    print("MIDI量化完成")



    # =====================
    # MIDI -> MusicXML
    # =====================

    musicxml = os.path.join(
        folder,
        "input.musicxml"
    )


    run([
        "python",
        "midi_to_musicxml.py",
        qmid,
        musicxml
    ])


    print("MusicXML完成")



    # =====================
    # CLEAN V27
    # =====================

    clean = os.path.join(
        folder,
        "clean.musicxml"
    )


    run([
        "python",
        "jianpu_fix_musicxml.py",
        "clean_musicxml.py",
        musicxml,
        clean
    ])


    print("清理完成")



    # =====================
    # jianpu_ly
    # =====================

    ly = os.path.join(
        folder,
        "output.ly"
    )


    print("開始 jianpu_ly")


    with open(
        ly,
        "w",
        encoding="utf-8"
    ) as f:


        result = subprocess.run(
            [
                "python",
                "-m",
                "jianpu_ly",
                clean
            ],
            stdout=f,
            stderr=subprocess.STDOUT,
            text=True
        )


    if result.returncode != 0:

        raise Exception(
            "jianpu_ly failed"
        )



    print("LY完成")



    # =====================
    # LilyPond PDF
    # =====================


    run([
        "lilypond",
        "--pdf",
        "-o",
        folder,
        ly
    ])



    pdf = os.path.join(
        folder,
        "output.pdf"
    )


    print("PDF完成")



    return FileResponse(
        pdf,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )



@app.get("/")
def home():

    return {
        "status":"JianpuTool running",
        "pipeline":
        "MP3 → MIDI → Quantize → MusicXML → Jianpu PDF"
    }