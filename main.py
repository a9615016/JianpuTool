import os
import uuid
import subprocess
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse


app = FastAPI()


BASE = "/app/outputs"


os.makedirs(BASE, exist_ok=True)


@app.get("/")
def home():

    return HTMLResponse("""
    <html>
    <head>
    <title>JianpuTool</title>
    </head>

    <body>

    <h2>JianpuTool</h2>

    <p>
    MP3 → MIDI → MusicXML → 簡譜 PDF
    </p>

    <form action="/upload" 
          method="post" 
          enctype="multipart/form-data">

    <input type="file" name="file">

    <button type="submit">
    Upload
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


    mp3 = os.path.join(
        outdir,
        file.filename
    )


    with open(mp3,"wb") as f:

        f.write(
            await file.read()
        )


    print("================")
    print("收到:")
    print(mp3)
    print("================")


    # -----------------------
    # MP3 → MIDI
    # -----------------------

    midi = os.path.join(
        outdir,
        "melody.mid"
    )


    print("開始 BasicPitch")


    subprocess.run(
        [
            "python",
            "basicpitch_convert.py",
            mp3,
            midi
        ],
        check=True
    )


    print("MIDI完成")



    # -----------------------
    # MIDI → MusicXML
    # -----------------------

    musicxml = os.path.join(
        outdir,
        "input.musicxml"
    )


    subprocess.run(
        [
            "python",
            "midi_to_musicxml.py",
            midi,
            musicxml
        ],
        check=True
    )


    print("MusicXML完成")



    # -----------------------
    # clean
    # -----------------------

    clean = os.path.join(
        outdir,
        "clean.musicxml"
    )


    subprocess.run(
        [
            "python",
            "clean_musicxml.py",
            musicxml,
            clean
        ],
        check=True
    )


    print("清理完成")



    # -----------------------
    # jianpu prepare
    # -----------------------

    ready = os.path.join(
        outdir,
        "jianpu_ready.musicxml"
    )


    subprocess.run(
        [
            "python",
            "jianpu_prepare.py",
            clean,
            ready
        ],
        check=True
    )


    print("Jianpu Prepare 完成")



    # -----------------------
    # jianpu_ly
    # -----------------------

    ly = os.path.join(
        outdir,
        "output.ly"
    )


    print("開始 jianpu_ly")


    with open(
        ly,
        "w",
        encoding="utf-8"
    ) as f:


        subprocess.run(
            [
                "python",
                "-m",
                "jianpu_ly",
                ready
            ],
            stdout=f,
            stderr=subprocess.STDOUT,
            check=True
        )


    print("LY完成")



    # -----------------------
    # LilyPond PDF
    # -----------------------

    print("開始 LilyPond")


    subprocess.run(
        [
            "lilypond",
            "-o",
            os.path.join(
                outdir,
                "jianpu"
            ),
            ly
        ],
        check=True
    )


    pdf = os.path.join(
        outdir,
        "jianpu.pdf"
    )


    print("PDF完成")



    return FileResponse(
        pdf,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )