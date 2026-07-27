from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import os
import uuid
import subprocess
import shutil


app = FastAPI()


BASE_DIR = "outputs"
os.makedirs(BASE_DIR, exist_ok=True)


@app.get("/")
def home():
    return {
        "status": "JianpuTool running",
        "api": ["/upload"]
    }



@app.post("/upload")
async def upload(file: UploadFile = File(...)):

    task_id = str(uuid.uuid4())

    work_dir = os.path.join(
        BASE_DIR,
        task_id
    )

    os.makedirs(work_dir)


    print("====================")
    print("開始任務:", task_id)



    # ======================
    # MP3
    # ======================

    mp3_file = os.path.join(
        work_dir,
        file.filename
    )


    with open(mp3_file, "wb") as f:
        shutil.copyfileobj(
            file.file,
            f
        )


    print("收到:", file.filename)
    print("MP3保存完成")
    print(mp3_file)



    # ======================
    # BasicPitch
    # ======================

    print("開始 BasicPitch")


    midi_file = os.path.join(
        work_dir,
        "melody.mid"
    )


    result = subprocess.run(
        [
            "python",
            "basicpitch_convert.py",
            mp3_file,
            midi_file
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


    print("MIDI完成")



    # ======================
    # MIDI -> MusicXML
    # ======================

    print("開始 MIDI轉MusicXML")


    musicxml = os.path.join(
        work_dir,
        "input.musicxml"
    )


    result = subprocess.run(
        [
            "python",
            "converter.py",
            midi_file,
            musicxml
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )


    print(result.stdout)


    if result.returncode != 0:
        return {
            "error":"MusicXML失敗",
            "log":result.stdout
        }


    print("MusicXML完成")



    # ======================
    # Clean MusicXML
    # ======================

    print("開始清理 MusicXML")


    clean_xml = os.path.join(
        work_dir,
        "clean.musicxml"
    )


    result = subprocess.run(
        [
            "python",
            "clean_musicxml.py",
            musicxml,
            clean_xml
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )


    print(result.stdout)


    if result.returncode != 0:
        return {
            "error":"清理失敗",
            "log":result.stdout
        }


    print("清理完成")



    # ======================
    # jianpu_ly
    # ======================

    print("開始 jianpu_ly")


    ly_file = os.path.join(
        work_dir,
        "jianpu.ly"
    )


    with open(
        ly_file,
        "w",
        encoding="utf-8"
    ) as f:


        result = subprocess.run(
            [
                "python",
                "-m",
                "jianpu_ly",
                "clean.musicxml"
            ],
            cwd=work_dir,
            stdout=f,
            stderr=subprocess.PIPE,
            text=True
        )


    print(
        "jianpu_ly return:",
        result.returncode
    )


    print(
        "jianpu_ly error:",
        result.stderr
    )


    if result.returncode != 0:

        return {
            "error":"jianpu_ly失敗",
            "log":result.stderr
        }



    if not os.path.exists(ly_file):

        return {
            "error":"jianpu.ly沒有產生"
        }


    print("jianpu.ly完成")



    # ======================
    # LilyPond
    # ======================

    print("開始 LilyPond")


    result = subprocess.run(
        [
            "lilypond",
            "-o",
            "jianpu",
            "jianpu.ly"
        ],
        cwd=work_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )


    print(result.stdout)


    if result.returncode != 0:

        return {
            "error":"LilyPond失敗",
            "log":result.stdout
        }



    pdf = os.path.join(
        work_dir,
        "jianpu.pdf"
    )


    if not os.path.exists(pdf):

        return {
            "error":"PDF不存在"
        }



    print("result = subprocess.run(result = subprocess.run(PDF完成")


    return FileResponse(
        pdf,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )