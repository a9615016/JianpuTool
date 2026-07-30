MAIN_VERSION = "V31-barfix"

print("================")
print(f"JianpuTool main.py {MAIN_VERSION}")
print("================")


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


OUTPUT_DIR = "/app/outputs"

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


@app.get("/")
def home():

    return {
        "status": "JianpuTool running",
        "version": MAIN_VERSION,
        "pipeline":
        "MP3/WAV → MIDI → MusicXML → clean_musicxml V31 → bar_check_fix → Jianpu PDF"
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


    ext = file.filename.lower().split(".")[-1]


    # ==========================
    # AUDIO → MIDI → MusicXML
    # ==========================

    if ext in ["mp3", "wav"]:

        print("AUDIO → BasicPitch")


        midi_file = os.path.join(
            job_dir,
            "melody.mid"
        )


        subprocess.run(
            [
                "python",
                "basicpitch_convert.py",
                input_file,
                midi_file
            ],
            check=True
        )


        xml_file = os.path.join(
            job_dir,
            "input.musicxml"
        )


        subprocess.run(
            [
                "python",
                "midi_to_musicxml.py",
                midi_file,
                xml_file
            ],
            check=True
        )


    # ==========================
    # MIDI → MusicXML
    # ==========================

    elif ext in ["mid", "midi"]:

        print("MIDI → MusicXML")


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


    # ==========================
    # MusicXML
    # ==========================

    elif ext in ["musicxml", "xml"]:

        print("MusicXML input")

        xml_file = input_file


    else:

        return {
            "error":
            "Unsupported file format"
        }



    # ==========================
    # CLEAN MUSICXML V31
    # ==========================

    clean_xml = os.path.join(
        job_dir,
        "clean.musicxml"
    )


    print(
        "RUN clean_musicxml.py V31"
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
    # BAR CHECK FIX
    # ==========================

    fixed_xml = os.path.join(
        job_dir,
        "fixed.musicxml"
    )


    print(
        "RUN bar_check_fix.py"
    )


    subprocess.run(
        [
            "python",
            "bar_check_fix.py",
            clean_xml,
            fixed_xml
        ],
        check=True
    )


    clean_xml = fixed_xml



    # ==========================
    # MusicXML → Jianpu LY
    # ==========================

    ly_file = os.path.join(
        job_dir,
        "output.ly"
    )


    print(
        "RUN jianpu_ly"
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

    print(
        "RUN LilyPond"
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


    return FileResponse(
        pdf_file,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )