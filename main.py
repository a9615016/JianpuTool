from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import os
import uuid
import subprocess


app = FastAPI()


BASE_DIR = "/app"

OUTPUT_DIR = "/app/outputs"

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


@app.get("/")
def home():

    return {
        "message":
        "JianpuTool MP3 → MIDI → MusicXML → Jianpu PDF"
    }



@app.post("/upload")
async def upload(
    file: UploadFile = File(...)
):

    job_id = str(uuid.uuid4())

    workdir = os.path.join(
        OUTPUT_DIR,
        job_id
    )


    os.makedirs(
        workdir,
        exist_ok=True
    )


    print("====================")
    print("開始任務:", job_id)


    # -------------------------
    # save mp3
    # -------------------------

    mp3_path = os.path.join(
        workdir,
        file.filename
    )


    with open(
        mp3_path,
        "wb"
    ) as f:

        f.write(
            await file.read()
        )


    print("MP3保存完成")
    print(mp3_path)



    # -------------------------
    # MP3 → MIDI
    # -------------------------

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


    print("MIDI完成")



    # -------------------------
    # MIDI → MusicXML
    # -------------------------

    musicxml_path = os.path.join(
        workdir,
        "input.musicxml"
    )


    print("開始 MIDI → MusicXML")


    subprocess.run(
        [
            "python",
            "midi_to_musicxml.py",
            midi_path,
            musicxml_path
        ],
        check=True
    )


    print("MusicXML完成")



    # -------------------------
    # Clean MusicXML
    # -------------------------

    clean_path = os.path.join(
        workdir,
        "clean.musicxml"
    )


    print("開始清理 MusicXML")


    subprocess.run(
        [
            "python",
            "clean_musicxml.py",
            musicxml_path,
            clean_path
        ],
        check=True
    )


    print("清理完成")



    # -------------------------
    # Jianpu LY
    # -------------------------

    print("開始 jianpu_ly")


    ly_path = os.path.join(
        workdir,
        "jianpu.ly"
    )


    with open(
        ly_path,
        "w"
    ) as out:


        subprocess.run(
            [
                "python",
                "-m",
                "jianpu_ly",
                clean_path
            ],
            stdout=out,
            stderr=subprocess.STDOUT,
            check=True
        )


    print("LY完成")



    # -------------------------
    # LilyPond PDF
    # -------------------------

    print("開始 LilyPond")


    subprocess.run(
        [
            "lilypond",
            "-o",
            os.path.join(
                workdir,
                "jianpu"
            ),
            ly_path
        ],
        check=True
    )


    pdf_path = os.path.join(
        workdir,
        "jianpu.pdf"
    )


    print("PDF完成")
    print(pdf_path)



    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )