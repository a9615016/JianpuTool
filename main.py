import os
import uuid
import subprocess
import shutil

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse


app = FastAPI()


BASE_DIR = "/app"

OUTPUT_DIR = "/app/outputs"


os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)



def run_cmd(cmd):

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



@app.get("/")
def home():

    return HTMLResponse(
        """
        <h2>JianpuTool</h2>

        <p>
        MP3 → BasicPitch MIDI → Jianpu PDF
        </p>

        <form action="/upload"
        enctype="multipart/form-data"
        method="post">

        <input name="file"
        type="file">

        <button>
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


    print("====================")
    print("開始任務:", job_id)
    print("收到:", file.filename)
    print("====================")



    # ----------------------
    # save mp3
    # ----------------------

    mp3_path = os.path.join(
        job_dir,
        file.filename
    )


    with open(mp3_path,"wb") as f:

        shutil.copyfileobj(
            file.file,
            f
        )


    print("MP3保存完成")
    print(mp3_path)



    # ----------------------
    # BasicPitch
    # ----------------------

    midi_path = os.path.join(
        job_dir,
        "melody.mid"
    )


    run_cmd(
        [
            "python",
            "basicpitch_convert.py",
            mp3_path,
            midi_path
        ]
    )


    print("MIDI完成")



    # ----------------------
    # CLEAN MIDI V2
    # ----------------------

    clean_mid = os.path.join(
        job_dir,
        "clean.mid"
    )


    run_cmd(
        [
            "python",
            "clean_midi.py",
            midi_path,
            clean_mid
        ]
    )


    midi_path = clean_mid


    print("clean MIDI完成")



    # ----------------------
    # MIDI → MusicXML
    # ----------------------

    xml_path = os.path.join(
        job_dir,
        "input.musicxml"
    )


    run_cmd(
        [
            "python",
            "midi_to_musicxml.py",
            midi_path,
            xml_path
        ]
    )


    print("MusicXML完成")



    # ----------------------
    # clean MusicXML
    # ----------------------

    clean_xml = os.path.join(
        job_dir,
        "clean.musicxml"
    )


    run_cmd(
        [
            "python",
            "clean_musicxml.py",
            xml_path,
            clean_xml
        ]
    )


    print("清理完成")



    # ----------------------
    # jianpu_ly
    # ----------------------

    ly_path = os.path.join(
        job_dir,
        "output.ly"
    )


    print("開始 jianpu_ly")


    with open(
        ly_path,
        "w",
        encoding="utf-8"
    ) as f:


        subprocess.run(
            [
                "python",
                "-m",
                "midi_to_jianpu_ly.py",
                clean_xml
            ],
            stdout=f,
            stderr=subprocess.STDOUT
        )



    print("LY完成")



    # ----------------------
    # LilyPond
    # ----------------------

    run_cmd(
        [
            "lilypond",
            "-o",
            job_dir,
            ly_path
        ]
    )


    pdf_path = ly_path.replace(
        ".ly",
        ".pdf"
    )


    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )