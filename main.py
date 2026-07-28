# main.py V32
# JianpuTool
# MP3 -> MIDI -> Clean MIDI -> MusicXML -> Jianpu PDF

import os
import uuid
import subprocess

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse


app = FastAPI()


OUTPUT_DIR = "/app/outputs"

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


print("MAIN VERSION V32 CLEAN MIDI ENABLE")



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
def index():

    return HTMLResponse("""
    <html>
    <body>

    <h2>JianpuTool</h2>

    <p>
    MP3 → 簡譜 PDF
    </p>

    <form action="/upload"
          method="post"
          enctype="multipart/form-data">

        <input type="file"
               name="file"
               accept=".mp3,.wav">

        <br><br>

        <button>
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

    task_id = str(uuid.uuid4())

    workdir = os.path.join(
        OUTPUT_DIR,
        task_id
    )

    os.makedirs(
        workdir,
        exist_ok=True
    )


    print("====================")
    print("MAIN VERSION V32 CLEAN MIDI ENABLE")
    print("開始任務:", task_id)
    print("收到:", file.filename)



    # ---------------------
    # MP3 save
    # ---------------------

    mp3_path = os.path.join(
        workdir,
        file.filename
    )


    with open(mp3_path,"wb") as f:

        f.write(
            await file.read()
        )


    print("MP3保存完成")
    print(mp3_path)



    # ---------------------
    # BasicPitch
    # ---------------------

    midi_path = os.path.join(
        workdir,
        "melody.mid"
    )


    run_cmd([
        "python",
        "basicpitch_convert.py",
        mp3_path,
        midi_path
    ])


    print("BasicPitch MIDI完成")



    # ---------------------
    # CLEAN MIDI
    # ---------------------

    clean_midi = os.path.join(
        workdir,
        "clean.mid"
    )


    run_cmd([
        "python",
        "clean_midi.py",
        midi_path,
        clean_midi
    ])


    print("CLEAN MIDI完成")



    # ---------------------
    # MIDI -> MusicXML
    # ---------------------

    xml_path = os.path.join(
        workdir,
        "input.musicxml"
    )


    run_cmd([
        "python",
        "midi_to_musicxml.py",
        clean_midi,
        xml_path
    ])


    print("MusicXML完成")



    # ---------------------
    # Clean MusicXML
    # ---------------------

    clean_xml = os.path.join(
        workdir,
        "clean.musicxml"
    )


    run_cmd([
        "python",
        "clean_musicxml.py",
        xml_path,
        clean_xml
    ])


    print("清理完成")



    # ---------------------
    # jianpu_ly
    # ---------------------

    ly_path = os.path.join(
        workdir,
        "jianpu.ly"
    )


    print("CHECK jianpu input:")
    print(clean_xml)

    print("開始 jianpu_ly")


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


    if result.returncode != 0:

        raise Exception(
            "jianpu_ly failed\n"+result.stdout
        )


    with open(
        ly_path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            result.stdout
        )


    print("LY完成")



    # ---------------------
    # LilyPond
    # ---------------------

    run_cmd([
        "lilypond",
        "-o",
        os.path.join(workdir,"jianpu"),
        ly_path
    ])



    pdf_path = os.path.join(
        workdir,
        "jianpu.pdf"
    )


    if not os.path.exists(pdf_path):

        raise Exception(
            "PDF不存在"
        )


    print("====================")
    print("SUCCESS")
    print(pdf_path)
    print("====================")


    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )