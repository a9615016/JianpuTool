from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse
import os
import uuid
import shutil
import subprocess


app = FastAPI()


BASE_DIR = "/app"

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "outputs"
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)



@app.get("/")
def home():

    return HTMLResponse(
        """
        <h2>JianpuTool 簡譜產生器</h2>

        <form action="/upload"
        method="post"
        enctype="multipart/form-data">

        <input type="file" name="file">

        <button type="submit">
        Upload
        </button>

        </form>
        """
    )



@app.post("/upload")
async def upload(
    file: UploadFile = File(...)
):


    job_id = str(uuid.uuid4())


    job_dir = os.path.join(
        OUTPUT_DIR,
        job_id
    )


    os.makedirs(
        job_dir,
        exist_ok=True
    )


    input_file = os.path.join(
        job_dir,
        file.filename
    )


    with open(
        input_file,
        "wb"
    ) as f:

        shutil.copyfileobj(
            file.file,
            f
        )


    print(
        "INPUT:",
        input_file
    )



    # ======================
    # MP3 -> MIDI
    # ======================

    midi_path = os.path.join(
        job_dir,
        "melody.mid"
    )


    print(
        "START MIDI EXTRACTION"
    )


    # 這裡接你原本 BasicPitch / melody extractor
    # 例如:
    #
    # python basicpitch_convert.py input.mp3 melody.mid
    #

    subprocess.run(
        [
            "python",
            "basicpitch_convert.py",
            input_file,
            midi_path
        ],
        check=True
    )



    print(
        "MIDI READY:",
        midi_path
    )



    # ======================
    # MIDI -> CLEAN MUSICXML
    # ======================


    clean_xml = os.path.join(
        job_dir,
        "clean.musicxml"
    )


    print(
        "START midi_to_musicxml_clean"
    )


    subprocess.run(
        [
            "python",
            "midi_to_musicxml_clean.py",
            midi_path,
            clean_xml
        ],
        check=True
    )


    print(
        "MusicXML READY:",
        clean_xml
    )



    # ======================
    # MusicXML -> Jianpu LY
    # ======================


    ly_file = os.path.join(
        job_dir,
        "jianpu.ly"
    )


    print(
        "START jianpu_ly"
    )


    with open(
        ly_file,
        "w",
        encoding="utf-8"
    ) as out:


        subprocess.run(
            [
                "python",
                "-m",
                "jianpu_ly",
                clean_xml
            ],
            stdout=out,
            stderr=subprocess.STDOUT,
            check=True
        )



    print(
        "LY READY:",
        ly_file
    )



    # ======================
    # LilyPond PDF
    # ======================


    print(
        "START LilyPond"
    )


    subprocess.run(
        [
            "lilypond",
            "-o",
            os.path.join(
                job_dir,
                "jianpu"
            ),
            ly_file
        ],
        check=True
    )



    pdf_file = os.path.join(
        job_dir,
        "jianpu.pdf"
    )


    print(
        "PDF DONE:",
        pdf_file
    )



    return FileResponse(
        pdf_file,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )