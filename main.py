import os
import uuid
import subprocess
import shutil

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse


app = FastAPI()


BASE = "/app/outputs"


os.makedirs(BASE, exist_ok=True)



@app.get("/")
def home():

    return {
        "status":"JianpuTool",
        "version":"V26 FINAL PIPELINE"
    }




@app.post("/upload")
async def upload(file: UploadFile = File(...)):


    job = str(uuid.uuid4())

    outdir = os.path.join(BASE, job)

    os.makedirs(outdir, exist_ok=True)



    input_audio = os.path.join(
        outdir,
        file.filename
    )


    with open(input_audio,"wb") as f:

        shutil.copyfileobj(
            file.file,
            f
        )



    print("================")
    print("收到:")
    print(input_audio)
    print("================")



    #
    # MP3 -> MIDI
    #

    midi_file = os.path.join(
        outdir,
        "melody.mid"
    )


    subprocess.run([

        "python",
        "basicpitch_convert.py",
        input_audio,
        midi_file

    ],check=True)



    print("MIDI完成")



    #
    # MIDI -> MusicXML
    #

    musicxml = os.path.join(
        outdir,
        "input.musicxml"
    )


    subprocess.run([

        "python",
        "midi_to_musicxml.py",
        midi_file,
        musicxml

    ],check=True)



    print("MusicXML完成")



    #
    # CLEAN V26
    #

    clean = os.path.join(
        outdir,
        "clean.musicxml"
    )


    subprocess.run([

        "python",
        "clean_musicxmlv40.py",
        musicxml,
        clean

    ],check=True)



    print("清理完成")



    #
    # JIANPU PREPARE
    #

    prepared = os.path.join(
        outdir,
        "prepared.musicxml"
    )


    subprocess.run([

        "python",
        "jianpu_prepare.py",
        clean,
        prepared

    ],check=True)



    print("jianpu prepare完成")



    #
    # MusicXML -> LY
    #

    ly_file = os.path.join(
        outdir,
        "score.ly"
    )


    with open(ly_file,"w") as f:

        subprocess.run([

            "python",
            "-m",
            "jianpu_ly",
            prepared

        ],
        stdout=f,
        stderr=subprocess.STDOUT,
        check=True
        )



    print("jianpu_ly完成")



    #
    # Lilypond PDF
    #

    subprocess.run([

        "lilypond",
        "-o",
        os.path.join(outdir,"jianpu"),
        ly_file

    ],check=True)



    pdf=os.path.join(
        outdir,
        "jianpu.pdf"
    )


    print("PDF完成")



    return FileResponse(
        pdf,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )