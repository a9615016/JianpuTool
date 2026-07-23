from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse
import os
import uuid
import subprocess

from music21 import converter


app = FastAPI()


# =====================
# 資料夾
# =====================

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)



# =====================
# 首頁
# =====================

@app.get("/", response_class=HTMLResponse)
def home():

<<<<<<< HEAD
    html = """
    <html>
    <head>
        <meta charset="utf-8">
        <title>JianpuTool</title>
    </head>

    <body>

    <h1>🎵 JianpuTool</h1>

    <h2>MIDI → 數字簡譜 PDF</h2>
=======
    return HTMLResponse(
        content="""
        <html>
        <head>
            <meta charset="utf-8">
            <title>JianpuTool</title>
        </head>
>>>>>>> 8fdda9500d7cf8fc5dcdde8ca75409f3a8f87b0f

        <body>

<<<<<<< HEAD
        <input type="file" name="file" accept=".mid,.midi">
=======
        <h1>🎵 JianpuTool MIDI → 簡譜</h1>
>>>>>>> 8fdda9500d7cf8fc5dcdde8ca75409f3a8f87b0f

        <form action="/midi" method="post" enctype="multipart/form-data">

<<<<<<< HEAD
        <button type="submit">
            產生簡譜 PDF
        </button>

    </form>


    </body>
    </html>
    """
=======
            <input type="file" name="file" accept=".mid,.midi">

            <br><br>

            <button type="submit">
                產生 MusicXML
            </button>

        </form>

        </body>
        </html>
        """
    )
>>>>>>> 8fdda9500d7cf8fc5dcdde8ca75409f3a8f87b0f

    return HTMLResponse(content=html)


<<<<<<< HEAD

=======
>>>>>>> 8fdda9500d7cf8fc5dcdde8ca75409f3a8f87b0f
# =====================
# 狀態
# =====================

@app.get("/status")
def status():

    return {
        "status": "JianpuTool running",
        "api": [
            "/midi"
        ]
    }



<<<<<<< HEAD

# =====================
# MIDI → MusicXML → Jianpu PDF
=======
# =====================
# MIDI → MusicXML
>>>>>>> 8fdda9500d7cf8fc5dcdde8ca75409f3a8f87b0f
# =====================

@app.post("/midi")
async def midi(file: UploadFile = File(...)):

    try:

<<<<<<< HEAD
        # -----------------
        # 儲存 MIDI
        # -----------------

        midi_name = (
            str(uuid.uuid4())
            + ".mid"
        )


        midi_path = os.path.join(
            UPLOAD_DIR,
            midi_name
        )
=======
        # 儲存 MIDI

        midi_name = (
            str(uuid.uuid4())
            + ".mid"
        )


        midi_path = os.path.join(
            UPLOAD_DIR,
            midi_name
        )


        with open(midi_path, "wb") as f:

            data = await file.read()

            f.write(data)
>>>>>>> 8fdda9500d7cf8fc5dcdde8ca75409f3a8f87b0f


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

        # MIDI 解析

        score = converter.parse(
            midi_path
        )


<<<<<<< HEAD
=======

        # 輸出 MusicXML

>>>>>>> 8fdda9500d7cf8fc5dcdde8ca75409f3a8f87b0f
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
        # MusicXML → jianpu .ly
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
        # LilyPond → PDF
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


        # -----------------
        # 回傳 PDF
        # -----------------

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
<<<<<<< HEAD
            "status": "error",
            "message": str(e)
=======

            "status": "error",

            "message": str(e)

>>>>>>> 8fdda9500d7cf8fc5dcdde8ca75409f3a8f87b0f
        }