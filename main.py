import os
import uuid
import subprocess

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse


app = FastAPI()


BASE_DIR = "/app"


@app.get("/")
def home():

    return HTMLResponse("""
    <html>
    <body>

    <h2>JianpuTool</h2>

    <h3>
    MP3 → MIDI → MusicXML → 簡譜 PDF
    </h3>

    <form action="/upload" 
          method="post" 
          enctype="multipart/form-data">

        <input type="file" name="file">

        <button>
        Convert
        </button>

    </form>

    </body>
    </html>
    """)



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

        raise Exception(
            result.stdout
        )

    return result.stdout



@app.post("/upload")
async def upload(
    file: UploadFile = File(...)
):


    task_id = str(uuid.uuid4())


    work_dir = os.path.join(
        BASE_DIR,
        "outputs",
        task_id
    )


    os.makedirs(
        work_dir,
        exist_ok=True
    )


    print("====================")
    print("開始任務:", task_id)
    print("收到:", file.filename)



    # =====================
    # MP3 save
    # =====================

    mp3 = os.path.join(
        work_dir,
        file.filename
    )


    with open(mp3,"wb") as f:

        f.write(
            await file.read()
        )


    print("MP3保存完成")
    print(mp3)



    # =====================
    # BasicPitch
    # =====================

    midi = os.path.join(
        work_dir,
        "melody.mid"
    )


    run_cmd([
        "python",
        "basicpitch_convert.py",
        mp3,
        midi
    ])


    print("MIDI完成")



    # =====================
    # MIDI -> MusicXML
    # =====================

    xml = os.path.join(
        work_dir,
        "input.musicxml"
    )


    run_cmd([
        "python",
        "midi_to_musicxml.py",
        midi,
        xml
    ])


    print("MusicXML完成")



    # =====================
    # CLEAN MUSICXML
    # =====================

    clean_xml = os.path.join(
        work_dir,
        "clean.musicxml"
    )


    run_cmd([
        "python",
        "jianpu_fix_musicxml.py",
        xml,
        clean_xml
    ])


    print("清理完成")



    # =============================
    # V26 TICK ALIGN FIX
    # =============================

    fixed_xml = os.path.join(
        work_dir,
        "jianpu_fixed.musicxml"
    )


    run_cmd([
        "python",
        "jianpu_fix_musicxml.py",
        clean_xml,
        fixed_xml
    ])


    print(
        "V26 FIX完成:",
        fixed_xml
    )



    # =====================
    # jianpu_ly
    # =====================

    ly_file = os.path.join(
        work_dir,
        "output.ly"
    )


    result = subprocess.run(
        [
            "python",
            "-m",
            "jianpu_ly",
            fixed_xml
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )


    print(result.stdout)


    if result.returncode != 0:

        return {
            "error":
            result.stdout
        }



    print(
        "jianpu_ly完成"
    )



    # =====================
    # LilyPond PDF
    # =====================

    run_cmd([
        "lilypond",
        "-o",
        os.path.join(
            work_dir,
            "jianpu"
        ),
        ly_file
    ])



    pdf = os.path.join(
        work_dir,
        "jianpu.pdf"
    )


    return {

        "status":
        "success",

        "pdf":
        pdf,

        "task":
        task_id

    }