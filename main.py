from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
import os
import uuid
import shutil
import subprocess


app = FastAPI()


OUTPUT_DIR = "/app/outputs"

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)



@app.get("/")
def home():

    return HTMLResponse(
        """
        <h2>JianpuTool 簡譜產生器</h2>

        <form action="/upload"
        method="post"
        enctype="multipart/form-data">

        <input type="file" name="file">

        <button>
        Upload
        </button>

        </form>
        """
    )



@app.post("/upload")
async def upload(
    file: UploadFile = File(...)
):

    job_id = str(uuid.uuid4())

    job_dir = os.path.join(
        OUTPUT_DIR,
        job_id
    )

    os.makedirs(
        job_dir,
        exist_ok=True
    )


    input_file = os.path.join(
        job_dir,
        file.filename
    )


    with open(
        input_file,
        "wb"
    ) as f:

        shutil.copyfileobj(
            file.file,
            f
        )


    print(
        "INPUT:",
        input_file
    )



    # =====================
    # MP3 -> MIDI
    # =====================

    midi_path = os.path.join(
        job_dir,
        "melody.mid"
    )


    print(
        "START MIDI"
    )


    subprocess.run(
        [
            "python",
            "basicpitch_convert.py",
            input_file,
            midi_path
        ],
        check=True
    )


    print(
        "MIDI READY",
        midi_path
    )



    # =====================
    # MIDI -> MusicXML
    # =====================

    clean_xml = os.path.join(
        job_dir,
        "clean.musicxml"
    )


    print(
        "START midi_to_musicxml_clean"
    )


    subprocess.run(
        [
            "python",
            "midi_to_musicxml_clean.py",
            midi_path,
            clean_xml
        ],
        check=True
    )


    print(
        "XML READY",
        clean_xml
    )



    if not os.path.exists(clean_xml):

        return JSONResponse(
            {
                "error":
                "沒有產生 musicxml"
            }
        )



    # =====================
    # MusicXML -> Jianpu LY
    # =====================


    ly_file = os.path.join(
        job_dir,
        "jianpu.ly"
    )


    print(
        "START jianpu_ly"
    )


    result = subprocess.run(
        [
            "python",
            "-m",
            "jianpu_ly",
            clean_xml
        ],
        capture_output=True,
        text=True
    )


    print(
        result.stdout
    )


    print(
        result.stderr
    )


    if result.returncode != 0:

        return JSONResponse(
            {
                "error":
                "jianpu_ly failed",
                "detail":
                result.stderr[-1000:]
            }
        )



    with open(
        ly_file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            result.stdout
        )



    if not os.path.exists(ly_file) or os.path.getsize(ly_file) == 0:

        return JSONResponse(
            {
                "error":
                "沒有產生 ly"
            }
        )


    print(
        "LY READY",
        ly_file,
        os.path.getsize(ly_file)
    )



    # =====================
    # LilyPond
    # =====================


    print(
        "START LilyPond"
    )


    subprocess.run(
        [
            "lilypond",
            "-o",
            os.path.join(
                job_dir,
                "jianpu"
            ),
            ly_file
        ],
        check=True
    )



    pdf_file = os.path.join(
        job_dir,
        "jianpu.pdf"
    )


    if not os.path.exists(pdf_file):

        return JSONResponse(
            {
                "error":
                "沒有產生 PDF"
            }
        )


    print(
        "PDF DONE",
        pdf_file
    )


    return FileResponse(
        pdf_file,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )