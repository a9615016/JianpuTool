from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse
import os
import uuid
import subprocess

from music21 import converter


app = FastAPI()


UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)



@app.get("/", response_class=HTMLResponse)
def home():

    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>JianpuTool</title>
    </head>

    <body>

    <h1>🎵 JianpuTool</h1>

    <h2>MIDI → 簡譜 PDF</h2>

    <form action="/midi"
          method="post"
          enctype="multipart/form-data">

        <input type="file"
               name="file"
               accept=".mid,.midi">

        <br><br>

        <button type="submit">
            產生簡譜 PDF
        </button>

    </form>

    </body>
    </html>
    """)



@app.get("/status")
def status():

    return {
        "status": "JianpuTool running",
        "api": [
            "/midi"
        ]
    }



@app.post("/midi")
async def midi(file: UploadFile = File(...)):

    try:

        # ======================
        # 儲存 MIDI
        # ======================

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



        # ======================
        # MIDI → MusicXML
        # ======================

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



        # ======================
        # MusicXML → jianpu ly
        # ======================

        ly_name = xml_name.replace(
            ".musicxml",
            ".ly"
        )


        ly_path = os.path.join(
            OUTPUT_DIR,
            ly_name
        )


        jianpu_result = subprocess.run(
            [
                "python",
                "-m",
                "jianpu_ly",
                xml_path
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )


        if jianpu_result.returncode != 0:

            return {
                "status": "jianpu_ly error",
                "error": jianpu_result.stderr.decode(
                    "utf-8",
                    errors="ignore"
                )
            }


        with open(
            ly_path,
            "wb"
        ) as f:

            f.write(
                jianpu_result.stdout
            )



        # ======================
        # LilyPond → PDF
        # ======================

        lily_result = subprocess.run(
            [
                "lilypond",
                "-o",
                ".",
                ly_name
            ],
            cwd=OUTPUT_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )


        if lily_result.returncode != 0:

            return {

                "status": "lilypond error",

                "stdout": lily_result.stdout.decode(
                    "utf-8",
                    errors="ignore"
                ),

                "stderr": lily_result.stderr.decode(
                    "utf-8",
                    errors="ignore"
                )
            }



        # ======================
        # 回傳 PDF
        # ======================

        pdf_name = ly_name.replace(
            ".ly",
            ".pdf"
        )


        pdf_path = os.path.join(
            OUTPUT_DIR,
            pdf_name
        )


        if not os.path.exists(pdf_path):

            return {

                "status": "error",

                "message": "PDF not generated",

                "files": os.listdir(
                    OUTPUT_DIR
                )

            }



        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=pdf_name
        )



    except Exception as e:

        return {

            "status": "python error",

            "error": str(e)

        }
