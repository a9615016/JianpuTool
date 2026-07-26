import os
import uuid
import shutil
import subprocess

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse


app = FastAPI()


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "outputs"
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)



@app.get("/")
async def home():

    with open(
        "index.html",
        encoding="utf-8"
    ) as f:

        return HTMLResponse(
            f.read()
        )



@app.post("/upload")
async def upload(
    file: UploadFile = File(...)
):

    job_id = str(uuid.uuid4())


    work_dir = os.path.join(
        OUTPUT_DIR,
        job_id
    )

    os.makedirs(
        work_dir,
        exist_ok=True
    )


    mp3 = os.path.join(
        work_dir,
        file.filename
    )


    print("================")
    print("收到:")
    print(file.filename)
    print("================")


    with open(mp3, "wb") as f:
        shutil.copyfileobj(
            file.file,
            f
        )


    print("MP3保存完成")



    ################################################
    # MP3 -> MIDI
    ################################################

    print("開始 BasicPitch")


    midi = os.path.join(
        work_dir,
        "melody.mid"
    )


    result = subprocess.run(
        [
            "python",
            "basicpitch_convert.py",
            mp3,
            midi
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )


    print(result.stdout)


    if result.returncode != 0:
        return {
            "error":"BasicPitch失敗",
            "log":result.stdout
        }



    ################################################
    # MIDI -> MusicXML
    ################################################

    print("MIDI轉MusicXML")


    xml = os.path.join(
        work_dir,
        "score.musicxml"
    )


    result = subprocess.run(
        [
            "python",
            "midi_to_musicxml.py",
            midi,
            xml
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )


    print(result.stdout)


    if result.returncode != 0:
        return {
            "error":"MusicXML產生失敗",
            "log":result.stdout
        }



    ################################################
    # Clean MusicXML
    ################################################

    print("清理 MusicXML")


    clean_xml = os.path.join(
        work_dir,
        "score_clean.musicxml"
    )


    result = subprocess.run(
        [
            "python",
            "clean_musicxml.py",
            xml,
            clean_xml
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )


    print(result.stdout)


    if result.returncode != 0:
        return {
            "error":"MusicXML清理失敗",
            "log":result.stdout
        }



    ################################################
    # MusicXML -> Jianpu
    ################################################

    print("產生簡譜")


    ly = os.path.join(
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


    print("jianpu_ly output:")
    print(result.stdout)


    if result.returncode != 0:
        return {
            "error":"jianpu_ly失敗",
            "log":result.stdout,
            "folder":work_dir
        }


    with open(
        ly,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(result.stdout)


    print("jianpu.ly完成")



    ################################################
    # LilyPond PDF
    ################################################

    print("LilyPond PDF")


    result = subprocess.run(
        [
            "lilypond",
            "-o",
            os.path.join(
                work_dir,
                "jianpu"
            ),
            ly
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )


    print(result.stdout)



    pdf = os.path.join(
        work_dir,
        "jianpu.pdf"
    )


    if os.path.exists(pdf):

        return FileResponse(
            pdf,
            media_type="application/pdf",
            filename="jianpu.pdf"
        )


    return {
        "error":"PDF產生失敗",
        "log":result.stdout,
        "folder":work_dir
    }





@app.post("/demucs")
async def demucs(
    file: UploadFile = File(...)
):

    return await upload(file)