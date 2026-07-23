from fastapi import FastAPI, UploadFile, File
<<<<<<< Updated upstream
from fastapi.responses import HTMLResponse, FileResponse
import os
import uuid
import subprocess

from music21 import converter

=======
from fastapi.responses import HTMLResponse
import os
>>>>>>> Stashed changes

app = FastAPI()


<<<<<<< Updated upstream
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

=======
# 取得目前 main.py 所在資料夾
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
>>>>>>> Stashed changes


@app.get("/", response_class=HTMLResponse)
def home():

<<<<<<< Updated upstream
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>JianpuTool</title>
    </head>

    <body>

    <h1>🎵 JianpuTool</h1>

    <h2>MIDI → 數字簡譜 PDF</h2>

    <form action="/midi" method="post" enctype="multipart/form-data">

        <input type="file" name="file" accept=".mid,.midi">

        <br><br>

        <button type="submit">
            產生簡譜 PDF
        </button>

    </form>

    </body>
    </html>
    """

    return HTMLResponse(content=html)

=======
    index_path = os.path.join(
        BASE_DIR,
        "static",
        "index.html"
    )

    with open(index_path, encoding="utf-8") as f:
        return f.read()
>>>>>>> Stashed changes


@app.get("/status")
def status():
    return {
        "status": "JianpuTool running",
        "api": [
            "/convert",
            "/midi"
        ]
    }


@app.post("/convert")
async def convert(file: UploadFile = File(...)):

    return {
        "filename": file.filename,
        "message": "convert api ready"
    }


@app.post("/midi")
async def midi(file: UploadFile = File(...)):

<<<<<<< Updated upstream
    try:

        # -----------------
        # MIDI 儲存
        # -----------------

        midi_name = str(uuid.uuid4()) + ".mid"

        midi_path = os.path.join(
            UPLOAD_DIR,
            midi_name
        )


        with open(
            midi_path,
            "wb"
        ) as f:

            f.write(
                await file.read()
            )



        # -----------------
        # MIDI → MusicXML
        # -----------------

        score = converter.parse(
            midi_path
        )


        xml_name = midi_name.replace(
            ".mid",
            ".musicxml"
        )


        xml_path = os.path.join(
            OUTPUT_DIR,
            xml_name
        )


        score.write(
            "musicxml",
            fp=xml_path
        )



        # -----------------
        # MusicXML → Jianpu LY
        # -----------------

        ly_name = xml_name.replace(
            ".musicxml",
            ".ly"
        )


        ly_path = os.path.join(
            OUTPUT_DIR,
            ly_name
        )


        with open(
            ly_path,
            "w",
            encoding="utf-8"
        ) as f:

            subprocess.run(
                [
                    "python",
                    "-m",
                    "jianpu_ly",
                    xml_path
                ],
                stdout=f,
                stderr=subprocess.PIPE,
                check=True
            )



        # -----------------
        # LY → PDF
        # -----------------

        subprocess.run(
            [
                "lilypond",
                "-o",
                OUTPUT_DIR,
                ly_path
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )



        pdf_name = ly_name.replace(
            ".ly",
            ".pdf"
        )


        pdf_path = os.path.join(
            OUTPUT_DIR,
            pdf_name
        )


        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=pdf_name
        )


    except subprocess.CalledProcessError as e:

        return {
            "status": "command error",
            "error": e.stderr.decode(
                "utf-8",
                errors="ignore"
            )
        }


    except Exception as e:

        return {
            "status": "error",
            "error": str(e)
        }
=======
    return {
        "filename": file.filename,
        "message": "midi api ready"
    }
>>>>>>> Stashed changes
