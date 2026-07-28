import os
import uuid
import subprocess

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse


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
    Upload MP3
    </button>

    </form>

    </body>
    </html>
    """)



@app.post("/upload")
async def upload(file: UploadFile = File(...)):


    job = str(uuid.uuid4())

    outdir = os.path.join(BASE, job)

    os.makedirs(outdir, exist_ok=True)


    mp3 = os.path.join(
        outdir,
        file.filename
    )


    with open(mp3,"wb") as f:
        f.write(await file.read())


    print("====================")
    print("開始任務:", job)
    print("收到:", file.filename)



    # ----------------------
    # MP3 -> MIDI
    # ----------------------

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



    # ----------------------
    # MIDI -> MusicXML
    # ----------------------

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



    # ----------------------
    # clean
    # ----------------------

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



    # ----------------------
    # force fix measure
    # ----------------------

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


    print("force fix 完成")



    # ----------------------
    # MusicXML -> Jianpu ly
    # ----------------------

    ly = os.path.join(
        outdir,
        "output.ly"
    )


    run([
        "python",
        "-m",
        "jianpu_ly",
        safe
    ])


    print("jianpu_ly完成")



    # jianpu_ly 預設輸出
    # 找 .ly

    for f in os.listdir(outdir):

        if f.endswith(".ly"):
            ly = os.path.join(outdir,f)
            break



    # ----------------------
    # Lilypond PDF
    # ----------------------

    run([
        "lilypond",
        "--pdf",
        ly
    ])


    print("PDF完成")



    pdf = ly.replace(
        ".ly",
        ".pdf"
    )


    return FileResponse(
        pdf,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )