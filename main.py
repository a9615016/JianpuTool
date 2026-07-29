from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import os
import uuid
import subprocess
import shutil


app = FastAPI(
    title="JianpuTool",
    version="1.0"
)


BASE_DIR = "/app"

OUTPUT_DIR = "/app/outputs"

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)



@app.get("/")
def home():

    return {
        "status": "JianpuTool running",
        "pipeline":
        "MP3/MIDI → MusicXML → clean_musicxml → Jianpu PDF"
    }



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


    with open(input_file, "wb") as f:

        shutil.copyfileobj(
            file.file,
            f
        )



    # ==========================
    # MIDI → MusicXML
    # ==========================

    if file.filename.endswith(
        ".mid"
    ):

        xml_file = os.path.join(
            job_dir,
            "input.musicxml"
        )


        subprocess.run(
            [
                "python",
                "midi_to_musicxml.py",
                input_file,
                xml_file
            ],
            check=True
        )


    else:

        xml_file = input_file



    # ==========================
    # CLEAN MUSICXML
    # ==========================

    clean_xml = os.path.join(
        job_dir,
        "clean.musicxml"
    )


    print(
        "RUN clean_musicxml.py"
    )


    subprocess.run(
        [
            "python",
            "clean_musicxml.py",
            xml_file,
            clean_xml
        ],
        check=True
    )



    # ==========================
    # MusicXML → Jianpu LY
    # ==========================

    ly_file = os.path.join(
        job_dir,
        "output.ly"
    )


    with open(
        ly_file,
        "w"
    ) as f:


        subprocess.run(
            [
                "python",
                "-m",
                "jianpu_ly",
                clean_xml
            ],
            stdout=f,
            stderr=subprocess.STDOUT,
            check=True
        )



    # ==========================
    # LilyPond PDF
    # ==========================

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


    return FileResponse(
        pdf_file,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )