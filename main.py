print("MAIN VERSION 20260726 QUANTIZE")
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse
import os
import uuid
import subprocess
import shutil


app = FastAPI()


BASE_DIR = os.getcwd()

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
        <html>
        <head>
        <title>JianpuTool</title>
        </head>

        <body>

        <h2>JianpuTool 簡譜產生器</h2>

        <p>
        MP3 → MIDI → MusicXML → 簡譜 PDF
        </p>

        <form action="/upload"
              method="post"
              enctype="multipart/form-data">

        <input type="file" name="file">

        <button type="submit">
        上傳轉換
        </button>

        </form>

        </body>
        </html>
        """
    )





@app.post("/upload")
async def upload(file: UploadFile = File(...)):


    job_id = str(uuid.uuid4())


    work_dir = os.path.join(
        OUTPUT_DIR,
        job_id
    )


    os.makedirs(
        work_dir,
        exist_ok=True
    )


    print("================")
    print("收到:")
    print(file.filename)
    print("================")



    # =========================
    # 保存 MP3
    # =========================

    input_audio = os.path.join(
        work_dir,
        file.filename
    )


    with open(
        input_audio,
        "wb"
    ) as f:

        shutil.copyfileobj(
            file.file,
            f
        )


    print("MP3保存完成")



    # =========================
    # BasicPitch
    # =========================

    print("開始 BasicPitch")


    midi_file = os.path.join(
        work_dir,
        "melody.mid"
    )


    result = subprocess.run(
        [
            "python",
            "basicpitch_convert.py",
            input_audio,
            midi_file
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )


    print(result.stdout)


    if result.returncode != 0:

        return {
            "error": result.stdout
        }



    print(
        "MIDI完成:",
        midi_file
    )



    # =========================
    # MIDI Quantize 新增
    # =========================

    print("開始 MIDI Quantize")


    clean_mid = os.path.join(
        work_dir,
        "melody_clean.mid"
    )


    result = subprocess.run(
        [
            "python",
            "midi_quantize.py",
            midi_file,
            clean_mid
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )


    print(result.stdout)


    if result.returncode != 0:

        return {
            "error": result.stdout
        }



    midi_file = clean_mid



    # =========================
    # MIDI → MusicXML
    # =========================

    print("MIDI轉MusicXML")


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
            "error": result.stdout
        }





    # =========================
    # MusicXML Clean V17
    # =========================

    print("清理 MusicXML")


    clean_xml = os.path.join(
        work_dir,
        "score_clean.musicxml"
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
            "error": result.stdout
        }





    # =========================
    # jianpu_ly
    # =========================

    print("產生簡譜")


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


    print("================")
    print(result.stderr)
    print(result.stdout)


    if result.returncode != 0:

        return {
            "error": result.stdout
        }



    return {
        "status": "success",
        "folder": work_dir
    }