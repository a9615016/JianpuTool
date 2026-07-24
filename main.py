from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse
import subprocess
import uuid
import os
import glob
import music21


app = FastAPI()


# ==========================
# LilyPond
# ==========================

if os.name == "nt":
    LILYPOND = r"C:\lilypond-2.26.0\bin\lilypond.exe"
else:
    LILYPOND = "lilypond"



# ==========================
# 首頁
# ==========================

@app.get("/")
def home():

    return HTMLResponse("""
    <html>
    <head>
    <meta charset="utf-8">
    <title>JianpuTool</title>
    </head>

    <body>

    <h1>🎵 JianpuTool</h1>

    <p>MusicXML / MIDI → 簡譜 PDF</p>


    <form action="/convert"
          method="post"
          enctype="multipart/form-data">

    <input type="file" name="file">

    <button>
    產生簡譜 PDF
    </button>

    </form>


    <br>

    <form action="/midi"
          method="post"
          enctype="multipart/form-data">

    <input type="file" name="file">

    <button>
    MIDI 轉簡譜 PDF
    </button>

    </form>


    </body>
    </html>
    """)



@app.get("/status")
def status():

    return {
        "status":"JianpuTool MVP OK"
    }



# ==========================
# MusicXML 清理
# ==========================

def clean_musicxml(input_file):

    output_file = input_file.replace(
        ".musicxml",
        "_clean.musicxml"
    )


    result = subprocess.run(
        [
            "python",
            "clean_musicxml.py",
            input_file,
            output_file
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )


    print(
        result.stdout,
        flush=True
    )


    if result.returncode != 0:

        return input_file


    print(
        "clean完成",
        flush=True
    )


    return output_file



# ==========================
# MusicXML → PDF
# ==========================

def musicxml_to_pdf(
    musicxml_file,
    work_dir
):

    clean_file = clean_musicxml(
        musicxml_file
    )


    ly_file = os.path.join(
        work_dir,
        "input.ly"
    )


    with open(
        ly_file,
        "w",
        encoding="utf-8"
    ) as out:


        result = subprocess.run(
            [
                "python",
                "-m",
                "jianpu_ly",
                clean_file
            ],
            stdout=out,
            stderr=subprocess.PIPE,
            text=True
        )


    print(
        "jianpu_ly:",
        result.returncode,
        flush=True
    )


    if result.returncode != 0:

        print(
            "===== jianpu_ly ERROR =====",
            flush=True
        )

        print(
            result.stderr,
            flush=True
        )

        print(
            "===========================",
            flush=True
        )


        return None, result.stderr



    result = subprocess.run(
        [
            LILYPOND,
            "input.ly"
        ],
        cwd=work_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )


    if result.returncode != 0:

        return None, result.stdout



    pdfs = glob.glob(
        os.path.join(
            work_dir,
            "*.pdf"
        )
    )


    if not pdfs:

        return None,"PDF not found"


    return pdfs[0],None




# ==========================
# MusicXML 上傳
# ==========================

@app.post("/convert")
async def convert(
    file: UploadFile = File(...)
):


    job = str(uuid.uuid4())


    work_dir = os.path.join(
        "outputs",
        job
    )


    os.makedirs(
        work_dir,
        exist_ok=True
    )


    musicxml_file = os.path.join(
        work_dir,
        "input.musicxml"
    )


    with open(
        musicxml_file,
        "wb"
    ) as f:

        f.write(
            await file.read()
        )



    pdf,error = musicxml_to_pdf(
        musicxml_file,
        work_dir
    )



    if error:

        return {
            "error":error
        }


    return FileResponse(
        pdf,
        filename="jianpu.pdf",
        media_type="application/pdf"
    )




# ==========================
# MIDI 上傳
# ==========================

@app.post("/midi")
async def midi_convert(
    file: UploadFile = File(...)
):


    job=str(uuid.uuid4())


    work_dir=os.path.join(
        "outputs",
        job
    )


    os.makedirs(
        work_dir,
        exist_ok=True
    )



    midi_file=os.path.join(
        work_dir,
        "input.mid"
    )


    musicxml_file=os.path.join(
        work_dir,
        "input.musicxml"
    )



    with open(
        midi_file,
        "wb"
    ) as f:

        f.write(
            await file.read()
        )



    try:

        score = music21.converter.parse(
            midi_file
        )


        score.write(
            "musicxml",
            fp=musicxml_file
        )


    except Exception as e:


        return {
            "error":"MIDI failed",
            "detail":str(e)
        }



    pdf,error = musicxml_to_pdf(
        musicxml_file,
        work_dir
    )


    if error:

        return {
            "error":error
        }



    return FileResponse(
        pdf,
        filename="jianpu.pdf",
        media_type="application/pdf"
    )