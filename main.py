import os
import uuid
import subprocess

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse


app = FastAPI()

OUTPUT_DIR = "/app/outputs"

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


def run(cmd):

    print("====================")
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



@app.get("/")
def home():

    return HTMLResponse("""
    <html>
    <body>

    <h2>JianpuTool</h2>

    <p>MP3 → MIDI → MusicXML → Jianpu PDF</p>

    <form action="/upload"
    method="post"
    enctype="multipart/form-data">

    <input type="file" name="file">

    <button>
    Upload
    </button>

    </form>

    </body>
    </html>
    """)



@app.post("/upload")
async def upload(
    file: UploadFile = File(...)
):

    task_id = str(uuid.uuid4())

    task_dir = os.path.join(
        OUTPUT_DIR,
        task_id
    )

    os.makedirs(
        task_dir,
        exist_ok=True
    )


    print("====================")
    print("開始任務:", task_id)
    print("收到:", file.filename)


    mp3 = os.path.join(
        task_dir,
        file.filename
    )


    with open(mp3, "wb") as f:
        f.write(
            await file.read()
        )


    print("MP3保存完成")
    print(mp3)



    # MP3 -> MIDI

    midi = os.path.join(
        task_dir,
        "melody.mid"
    )


    run([
        "python",
        "basicpitch_convert.py",
        mp3,
        midi
    ])


    print("MIDI完成")



    # MIDI -> MusicXML

    musicxml = os.path.join(
        task_dir,
        "input.musicxml"
    )


    run([
        "python",
        "midi_to_musicxml.py",
        midi,
        musicxml
    ])


    print("MusicXML完成")



    # clean

    clean = os.path.join(
        task_dir,
        "clean.musicxml"
    )


    run([
        "python",
        "clean_musicxml.py",
        musicxml,
        clean
    ])


    print("清理完成")



    # NEW STEP
    # 修正 jianpu_ly 小節錯誤

    safe = os.path.join(
        task_dir,
        "safe.musicxml"
    )


    run([
        "python",
        "force_fix_measure.py",
        clean,
        safe
    ])


    print("小節修正完成")



    print("CHECK jianpu input:")
    print(safe)



    # MusicXML -> Jianpu LilyPond

    print("開始 jianpu_ly")


    run([
        "python",
        "-m",
        "jianpu_ly",
        safe
    ])



    ly = safe.replace(
        ".musicxml",
        ".ly"
    )


    print("LY:", ly)



    # LilyPond PDF

    print("開始 LilyPond")


    output_base = os.path.join(
        task_dir,
        "jianpu"
    )


    run([
        "lilypond",
        "-o",
        output_base,
        ly
    ])



    pdf = output_base + ".pdf"


    if not os.path.exists(pdf):

        raise Exception(
            "PDF產生失敗"
        )


    print("====================")
    print("PDF完成")
    print(pdf)


    return FileResponse(
        pdf,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )