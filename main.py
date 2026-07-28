import os
import uuid
import subprocess

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse


app = FastAPI()


BASE_DIR = "/app"
OUTPUT_DIR = "/app/outputs"


os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


@app.get("/")
def home():

    return HTMLResponse("""
    <html>
    <body>

    <h2>JianpuTool</h2>

    <form action="/upload"
          method="post"
          enctype="multipart/form-data">

    <input type="file" name="file">

    <button type="submit">
    Convert
    </button>

    </form>

    </body>
    </html>
    """)



@app.post("/upload")
async def upload(
    file: UploadFile = File(...)
):

    job = str(uuid.uuid4())

    workdir = os.path.join(
        OUTPUT_DIR,
        job
    )

    os.makedirs(
        workdir,
        exist_ok=True
    )


    print("====================")
    print("開始任務:", job)
    print("收到:", file.filename)


    mp3 = os.path.join(
        workdir,
        file.filename
    )


    with open(mp3,"wb") as f:
        f.write(
            await file.read()
        )


    print("MP3保存完成")


    # =====================
    # BasicPitch
    # =====================

    midi = os.path.join(
        workdir,
        "melody.mid"
    )


    cmd = [
        "python",
        "basicpitch_convert.py",
        mp3,
        midi
    ]


    print("RUN:", " ".join(cmd))

    subprocess.run(
        cmd,
        check=True
    )


    print("MIDI完成")



    # =====================
    # MIDI -> MusicXML
    # =====================

    musicxml = os.path.join(
        workdir,
        "input.musicxml"
    )


    cmd = [
        "python",
        "midi_to_musicxml.py",
        midi,
        musicxml
    ]


    print("RUN:", " ".join(cmd))

    subprocess.run(
        cmd,
        check=True
    )


    print("MusicXML完成")



    # =====================
    # clean
    # =====================

    clean_xml = os.path.join(
        workdir,
        "clean.musicxml"
    )


    cmd = [
        "python",
        "clean_musicxml.py",
        musicxml,
        clean_xml
    ]


    print("RUN:", " ".join(cmd))


    subprocess.run(
        cmd,
        check=True
    )


    print("清理完成")



    # =====================
    # patch_jianpu
    # =====================

    patched_xml = os.path.join(
        workdir,
        "patched.musicxml"
    )


    cmd = [
        "python",
        "patch_jianpu.py",
        clean_xml,
        patched_xml
    ]


    print("RUN:", " ".join(cmd))


    subprocess.run(
        cmd,
        check=True
    )


    print("Patch完成")



    # =====================
    # jianpu_ly
    # =====================

    ly_file = os.path.join(
        workdir,
        "score.ly"
    )


    cmd = [
        "python",
        "-m",
        "jianpu_ly",
        patched_xml
    ]


    print("RUN:", " ".join(cmd))


    with open(
        ly_file,
        "w"
    ) as f:

        subprocess.run(
            cmd,
            stdout=f,
            stderr=subprocess.STDOUT,
            check=True
        )


    print("LY完成")



    # =====================
    # LilyPond PDF
    # =====================

    cmd = [
        "lilypond",
        "-o",
        os.path.join(workdir,"jianpu"),
        ly_file
    ]


    print("RUN:", " ".join(cmd))


    subprocess.run(
        cmd,
        check=True
    )


    pdf = os.path.join(
        workdir,
        "jianpu.pdf"
    )


    print("PDF完成")
    print(pdf)


    return FileResponse(
        pdf,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )