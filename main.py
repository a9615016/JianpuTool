from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse
import os
import uuid
import subprocess
import shutil


app = FastAPI()


BASE = "/app/outputs"


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
        raise Exception(result.stdout)

    return result.stdout



@app.get("/")
def home():

    return HTMLResponse("""
    <html>
    <body>

    <h2>JianpuTool 簡譜產生器</h2>

    <form action="/upload" method="post" enctype="multipart/form-data">

    <input type="file" name="file">

    <button type="submit">
    上傳 MP3
    </button>

    </form>

    </body>
    </html>
    """)



@app.post("/upload")
async def upload(file: UploadFile = File(...)):


    job = str(uuid.uuid4())

    outdir = os.path.join(
        BASE,
        job
    )

    os.makedirs(
        outdir,
        exist_ok=True
    )


    print("====================")
    print("開始任務:", job)
    print("收到:", file.filename)



    mp3 = os.path.join(
        outdir,
        file.filename
    )


    with open(mp3,"wb") as f:
        shutil.copyfileobj(
            file.file,
            f
        )


    print("MP3保存完成")
    print(mp3)



    # =====================
    # MP3 -> MIDI
    # =====================

    midi = os.path.join(
        outdir,
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
    # MIDI -> MusicXML
    # =====================

    musicxml = os.path.join(
        outdir,
        "input.musicxml"
    )


    run([
        "python",
        "midi_to_musicxml.py",
        midi,
        musicxml
    ])


    print("MusicXML完成")



    # =====================
    # CLEAN
    # =====================

    clean = os.path.join(
        outdir,
        "clean.musicxml"
    )


    run([
        "python",
        "clean_musicxml.py",
        musicxml,
        clean
    ])


    print("清理完成")



    # =====================
    # FORCE FIX MEASURE
    # =====================

    safe = os.path.join(
        outdir,
        "safe.musicxml"
    )


    run([
        "python",
        "force_fix_measure.py",
        clean,
        safe
    ])


    print("小節修正完成")



    # =====================
    # MUSICXML -> LY
    # =====================

    ly = os.path.join(
        outdir,
        "jianpu.ly"
    )


    result = subprocess.run(
        [
            "python",
            "-m",
            "jianpu_ly",
            safe
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )


    print(result.stdout)


    if result.returncode != 0:

        return {
            "error":
            "jianpu_ly failed",
            "log":
            result.stdout
        }



    print("LY完成")



    # =====================
    # Lilypond PDF
    # =====================

    run([
        "lilypond",
        "-o",
        os.path.join(outdir,"jianpu"),
        ly
    ])


    pdf = os.path.join(
        outdir,
        "jianpu.pdf"
    )


    if os.path.exists(pdf):

        return FileResponse(
            pdf,
            media_type="application/pdf"
        )


    return {
        "status":"完成",
        "folder":outdir
    }