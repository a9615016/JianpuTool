import os
import uuid
import glob
import subprocess
import shutil

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse


app = FastAPI()


BASE_DIR = "/app"
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

os.makedirs(OUTPUT_DIR, exist_ok=True)


def run_command(cmd, cwd=None):

    print("執行:", " ".join(cmd))

    result = subprocess.run(
        cmd,
        cwd=cwd,
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

        <h2>JianpuTool MP3 → 簡譜</h2>

        <form action="/convert"
              method="post"
              enctype="multipart/form-data">

        <input type="file"
               name="file"
               accept=".mp3,.wav">

        <button type="submit">
        轉換
        </button>

        </form>

        </body>
        </html>
        """
    )



@app.post("/convert")
async def convert(
    file: UploadFile = File(...)
):

    job_id = str(uuid.uuid4())

    work_dir = os.path.join(
        OUTPUT_DIR,
        job_id
    )

    os.makedirs(work_dir)


    # -------------------------
    # 儲存 MP3
    # -------------------------

    input_audio = os.path.join(
        work_dir,
        file.filename
    )


    with open(input_audio, "wb") as f:
        shutil.copyfileobj(
            file.file,
            f
        )


    print("輸入:", input_audio)



    # -------------------------
    # 1. Demucs
    # -------------------------

    print("開始 Demucs")


    run_command(
        [
            "python",
            "-m",
            "demucs",
            "-n",
            "htdemucs",
            input_audio
        ]
    )


    vocals_list = glob.glob(
        "separated/**/vocals.wav",
        recursive=True
    )


    if not vocals_list:

        raise Exception(
            "Demucs 沒有產生 vocals.wav"
        )


    vocals = vocals_list[0]


    print(
        "找到 vocals:",
        vocals
    )



    # -------------------------
    # 2. BasicPitch
    # -------------------------

    melody_mid = os.path.join(
        work_dir,
        "melody.mid"
    )


    print(
        "開始 BasicPitch"
    )


    run_command(
        [
            "python",
            "melody_from_audio.py",
            vocals,
            melody_mid
        ]
    )



    # -------------------------
    # 3. MIDI → MusicXML
    # -------------------------

    musicxml = os.path.join(
        work_dir,
        "melody.musicxml"
    )


    print(
        "開始 MIDI → MusicXML"
    )


    run_command(
        [
            "python",
            "midi_to_musicxml.py",
            melody_mid,
            musicxml
        ]
    )



    # -------------------------
    # 4. 清理 MusicXML
    # -------------------------

    clean_xml = os.path.join(
        work_dir,
        "clean.musicxml"
    )


    run_command(
        [
            "python",
            "clean_musicxml.py",
            musicxml,
            clean_xml
        ]
    )



    # -------------------------
    # 5. jianpu_ly
    # -------------------------

    ly_file = os.path.join(
        work_dir,
        "jianpu.ly"
    )


    print(
        "開始 jianpu_ly"
    )


    with open(
        ly_file,
        "w",
        encoding="utf-8"
    ) as f:

        subprocess.run(
            [
                "python",
                "-m",
                "jianpu_ly",
                clean_xml
            ],
            stdout=f,
            stderr=subprocess.STDOUT,
            text=True
        )



    # -------------------------
    # 6. LilyPond PDF
    # -------------------------

    print(
        "開始 LilyPond"
    )


    run_command(
        [
            "lilypond",
            "-o",
            os.path.join(
                work_dir,
                "jianpu"
            ),
            ly_file
        ]
    )


    pdf_file = os.path.join(
        work_dir,
        "jianpu.pdf"
    )


    if not os.path.exists(pdf_file):

        raise Exception(
            "PDF產生失敗"
        )


    return FileResponse(
        pdf_file,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )



@app.get("/health")
def health():

    return {
        "status":"JianpuTool running"
    }