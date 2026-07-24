import os
import uuid
import shutil
import subprocess

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse


app = FastAPI()


BASE_DIR = "outputs"

os.makedirs(
    BASE_DIR,
    exist_ok=True
)


# ==========================
# 首頁
# ==========================

@app.get("/", response_class=HTMLResponse)
def home():

    return """
    <html>
    <head>
    <meta charset="utf-8">
    <title>JianpuTool</title>
    </head>

    <body>

    <h1>JianpuTool</h1>


    <h3>MusicXML → 簡譜 PDF</h3>

    <form action="/convert"
    method="post"
    enctype="multipart/form-data">

    <input type="file"
    name="file"
    accept=".musicxml,.xml">

    <button>
    轉換簡譜
    </button>

    </form>


    <hr>


    <h3>MIDI → 簡譜 PDF</h3>


    <form action="/midi"
    method="post"
    enctype="multipart/form-data">

    <input type="file"
    name="file"
    accept=".mid">

    <button>
    MIDI轉簡譜
    </button>

    </form>


    </body>
    </html>
    """



# ==========================
# status
# ==========================

@app.get("/status")
def status():

    return {
        "status":"JianpuTool running",
        "api":[
            "/convert",
            "/midi"
        ]
    }



# ==========================
# 執行 subprocess 工具
# ==========================

def run_cmd(cmd):

    print("RUN:")
    print(cmd)


    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )


    print("STDOUT:")
    print(result.stdout)


    print("STDERR:")
    print(result.stderr)


    if result.returncode != 0:

        raise Exception(
            result.stderr
        )


    return result



# ==========================
# 產生 PDF
# ==========================

def generate_pdf(workdir, musicxml):


    clean_file = os.path.join(
        workdir,
        "clean.musicxml"
    )


    rebuild_file = os.path.join(
        workdir,
        "rebuild.musicxml"
    )


    ly_file = os.path.join(
        workdir,
        "jianpu.ly"
    )



    print("開始 clean MusicXML")


    run_cmd(
        [
            "python",
            "clean_musicxml.py",
            musicxml,
            clean_file
        ]
    )



    print("開始 rebuild MusicXML")


    run_cmd(
        [
            "python",
            "rebuild_musicxml.py",
            clean_file,
            rebuild_file
        ]
    )



    print("開始 jianpu_ly")


    with open(
        ly_file,
        "w",
        encoding="utf-8"
    ) as f:


        f.write(
            '\\version "2.24.4"\n'
        )


        result = subprocess.run(
            [
                "python",
                "-m",
                "jianpu_ly",
                rebuild_file
            ],

            stdout=f,

            stderr=subprocess.PIPE,

            text=True
        )


    print(
        "jianpu_ly:",
        result.returncode
    )


    print(
        result.stderr
    )


    if result.returncode != 0:

        raise Exception(
            result.stderr
        )



    print("開始 LilyPond")


    run_cmd(
        [
            "lilypond",
            "-o",
            os.path.join(
                workdir,
                "jianpu"
            ),
            ly_file
        ]
    )


    pdf = os.path.join(
        workdir,
        "jianpu.pdf"
    )


    return pdf




# ==========================
# MusicXML
# ==========================

@app.post("/convert")
async def convert(
    file: UploadFile = File(...)
):


    job = str(
        uuid.uuid4()
    )


    workdir = os.path.join(
        BASE_DIR,
        job
    )


    os.makedirs(
        workdir,
        exist_ok=True
    )


    input_file = os.path.join(
        workdir,
        "input.musicxml"
    )



    with open(
        input_file,
        "wb"
    ) as f:

        shutil.copyfileobj(
            file.file,
            f
        )



    pdf = generate_pdf(
        workdir,
        input_file
    )


    return FileResponse(
        pdf,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )





# ==========================
# MIDI
# ==========================

@app.post("/midi")
async def midi_convert(
    file: UploadFile = File(...)
):


    job = str(
        uuid.uuid4()
    )


    workdir = os.path.join(
        BASE_DIR,
        job
    )


    os.makedirs(
        workdir,
        exist_ok=True
    )



    midi_file = os.path.join(
        workdir,
        "input.mid"
    )


    with open(
        midi_file,
        "wb"
    ) as f:

        shutil.copyfileobj(
            file.file,
            f
        )



    print(
        "開始 MIDI → MusicXML"
    )


    run_cmd(
        [
            "python",
            "converter.py",
            midi_file
        ]
    )



    musicxml = os.path.splitext(
        midi_file
    )[0] + ".musicxml"



    pdf = generate_pdf(
        workdir,
        musicxml
    )



    return FileResponse(
        pdf,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )