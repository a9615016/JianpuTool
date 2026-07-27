import os
import uuid
import subprocess

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse


app = FastAPI()


BASE = "outputs"

os.makedirs(BASE, exist_ok=True)



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
        raise Exception(result.stdout)

    return result.stdout



@app.get("/")
def home():

    return HTMLResponse(
        """
        <html>
        <body>

        <h2>
        JianpuTool 簡譜產生器
        </h2>

        <p>
        MP3 → MIDI → Jianpu PDF
        </p>

        <form action="/upload"
              method="post"
              enctype="multipart/form-data">

        <input type="file"
               name="file">

        <button>
        Convert
        </button>

        </form>

        </body>
        </html>
        """
    )




@app.post("/upload")
async def upload(file: UploadFile = File(...)):


    task_id = str(uuid.uuid4())

    work_dir = os.path.join(
        BASE,
        task_id
    )

    os.makedirs(work_dir)



    print("====================")
    print("開始任務:", task_id)
    print("====================")



    # ------------------------
    # MP3
    # ------------------------

    mp3 = os.path.join(
        work_dir,
        file.filename
    )


    with open(mp3,"wb") as f:
        f.write(
            await file.read()
        )


    print("MP3保存完成")
    print(mp3)



    # ------------------------
    # BasicPitch
    # ------------------------

    midi = os.path.join(
        work_dir,
        "melody.mid"
    )


    run_cmd(
        [
            "python",
            "basicpitch_convert.py",
            mp3,
            midi
        ]
    )


    print("MIDI完成")



    # ------------------------
    # MIDI CLEANER V29
    # ------------------------

    clean_mid = os.path.join(
        work_dir,
        "clean.mid"
    )


    run_cmd(
        [
            "python",
            "midi_cleaner.py",
            midi,
            clean_mid
        ]
    )


    print("MIDI CLEAN完成")



    # ------------------------
    # MIDI → MusicXML
    # ------------------------

    musicxml = os.path.join(
        work_dir,
        "input.musicxml"
    )


    run_cmd(
        [
            "python",
            "midi_to_musicxml.py",
            clean_mid,
            musicxml
        ]
    )


    print("MusicXML完成")



    # ------------------------
    # CLEAN MUSICXML
    # ------------------------

    clean_xml = os.path.join(
        work_dir,
        "clean.musicxml"
    )


    run_cmd(
        [
            "python",
            "clean_musicxml.py",
            musicxml,
            clean_xml
        ]
    )


    print("清理完成")



    # ------------------------
    # Jianpu LY
    # ------------------------

    ly_file = os.path.join(
        work_dir,
        "jianpu.ly"
    )


    result = subprocess.run(
        [
            "python",
            "-m",
            "jianpu_ly",
            clean_xml
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )


    print(result.stdout)



    with open(
        ly_file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            result.stdout
        )



    if result.returncode != 0:

        return {
            "error":
            result.stdout
        }



    print("LY完成")



    # ------------------------
    # LilyPond PDF
    # ------------------------

    pdf = os.path.join(
        work_dir,
        "jianpu.pdf"
    )


    run_cmd(
        [
            "lilypond",
            "-o",
            os.path.join(work_dir,"jianpu"),
            ly_file
        ]
    )


    return FileResponse(
        os.path.join(
            work_dir,
            "jianpu.pdf"
        ),
        media_type="application/pdf"
    )