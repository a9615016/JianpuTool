from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import os
import uuid
import subprocess
import shutil


app = FastAPI(
    title="JianpuTool MIDI Direct"
)


BASE_DIR = "/app/outputs"


os.makedirs(
    BASE_DIR,
    exist_ok=True
)



@app.get("/")
def home():

    return {
        "status": "JianpuTool running",
        "pipeline":
        "Audio -> MIDI -> LY -> PDF"
    }




@app.post("/upload")
async def upload(
    file: UploadFile = File(...)
):

    job = str(uuid.uuid4())


    out_dir = os.path.join(
        BASE_DIR,
        job
    )


    os.makedirs(
        out_dir,
        exist_ok=True
    )


    input_file = os.path.join(
        out_dir,
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



    print("INPUT:")
    print(input_file)



    # =========================
    # Step 1
    # MP3 -> MIDI
    # =========================

    midi_file = os.path.join(
        out_dir,
        "melody.mid"
    )


    print("START MIDI EXTRACTION")



    subprocess.run(
        [
            "python",
            "voice_to_midi.py",
            input_file,
            midi_file
        ],
        check=True
    )



    print("MIDI DONE")
    print(midi_file)




    # =========================
    # Step 2
    # MIDI -> LilyPond
    # =========================


    ly_file = os.path.join(
        out_dir,
        "melody.ly"
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



    print("LY DONE")
    print(ly_file)




    # =========================
    # Step 3
    # LilyPond PDF
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



    pdf_file = os.path.join(
        out_dir,
        "melody.pdf"
    )



    if not os.path.exists(pdf_file):

        # lilypond 預設名稱
        generated = ly_file.replace(
            ".ly",
            ".pdf"
        )

        if os.path.exists(generated):

            pdf_file = generated



    print("PDF DONE")
    print(pdf_file)



    return FileResponse(
        pdf_file,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )