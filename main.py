from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse
import os
import uuid
import shutil
import subprocess


print("========== JIANPUTOOL V91 DIRECT MIDI ==========")


app = FastAPI(
    title="JianpuTool V91"
)


BASE_DIR = "/app/outputs"

os.makedirs(BASE_DIR, exist_ok=True)



@app.get("/")
def home():

    return HTMLResponse(
        """
        <h2>JianpuTool V91</h2>

        <p>MP3/WAV → MIDI → Jianpu PDF</p>

        <form action="/upload"
              enctype="multipart/form-data"
              method="post">

            <input type="file" name="file">

            <button type="submit">
                Convert
            </button>

        </form>
        """
    )



@app.post("/upload")
async def upload(
    file: UploadFile = File(...)
):

    job_id = str(uuid.uuid4())


    out_dir = os.path.join(
        BASE_DIR,
        job_id
    )

    os.makedirs(
        out_dir,
        exist_ok=True
    )


    input_file = os.path.join(
        out_dir,
        file.filename
    )


    with open(input_file, "wb") as f:

        shutil.copyfileobj(
            file.file,
            f
        )


    print("======================")
    print("INPUT")
    print(input_file)
    print("======================")



    # =========================
    # 1. AUDIO -> MIDI
    # =========================

    midi_file = os.path.join(
        out_dir,
        "melody.mid"
    )


    print("START AUDIO TO MIDI")


    subprocess.run(
        [
            "python",
            "voice_to_midi.py",
            input_file,
            midi_file
        ],
        check=True
    )


    print("MIDI CREATED")
    print(midi_file)



    # =========================
    # 2. MIDI -> JIANPU LY
    # =========================

    ly_file = os.path.join(
        out_dir,
        "jianpu.ly"
    )


    print("MIDI DIRECT TO JIANPU LY")


    subprocess.run(
        [
            "python",
            "midi_to_jianpu_ly.py",
            midi_file,
            ly_file
        ],
        check=True
    )


    print("LY CREATED")
    print(ly_file)



    # =========================
    # 3. LY -> PDF
    # =========================

    print("RUN LILYPOND")


    subprocess.run(
        [
            "lilypond",
            "--pdf",
            ly_file
        ],
        cwd=out_dir,
        check=True
    )


    pdf_file = ly_file.replace(
        ".ly",
        ".pdf"
    )


    if not os.path.exists(pdf_file):

        raise Exception(
            "PDF NOT CREATED"
        )


    print("PDF DONE")
    print(pdf_file)



    return FileResponse(
        pdf_file,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )