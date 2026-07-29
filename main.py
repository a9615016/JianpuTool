import os
import uuid
import subprocess
import shutil

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse


app = FastAPI()


print("######## MAIN V2 VERSION ########")


BASE_DIR = "/app"
OUTPUT_DIR = "/app/outputs"

os.makedirs(OUTPUT_DIR, exist_ok=True)



def run_cmd(cmd, cwd=None):

    print("RUN:", " ".join(cmd))

    result = subprocess.run(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    print(result.stdout)

    if result.returncode != 0:
        raise Exception(result.stdout)

    return result.stdout



@app.get("/")
def home():

    return {
        "status": "JianpuTool",
        "version": "MAIN V2 + PREPARE V3"
    }




@app.post("/upload")
async def upload(file: UploadFile = File(...)):


    job_id = str(uuid.uuid4())

    job_dir = os.path.join(
        OUTPUT_DIR,
        job_id
    )

    os.makedirs(job_dir, exist_ok=True)


    print("====================")
    print("開始任務:", job_id)
    print("收到:", file.filename)



    # -----------------------
    # Save MP3
    # -----------------------

    mp3_path = os.path.join(
        job_dir,
        file.filename
    )


    with open(mp3_path, "wb") as f:
        shutil.copyfileobj(
            file.file,
            f
        )


    print("MP3保存完成")
    print(mp3_path)



    # -----------------------
    # MP3 -> MIDI
    # -----------------------

    midi_path = os.path.join(
        job_dir,
        "melody.mid"
    )


    run_cmd([
        "python",
        "basicpitch_convert.py",
        mp3_path,
        midi_path
    ])


    print("MIDI完成")



    # -----------------------
    # MIDI -> MusicXML
    # -----------------------

    xml_path = os.path.join(
        job_dir,
        "input.musicxml"
    )


    run_cmd([
        "python",
        "midi_to_musicxml.py",
        midi_path,
        xml_path
    ])


    print("MusicXML完成")



    # -----------------------
    # Jianpu Prepare V3
    # -----------------------

    clean_xml = os.path.join(
        job_dir,
        "clean.musicxml"
    )


    run_cmd([
        "python",
        "jianpu_prepare_v3.py",
        xml_path,
        clean_xml
    ])


    print("清理完成")



    # -----------------------
    # MusicXML -> Jianpu LY
    # -----------------------

    ly_path = os.path.join(
        job_dir,
        "output.ly"
    )


    print("CHECK jianpu input:")
    print(clean_xml)


    run_cmd([
        "python",
        "-m",
        "jianpu_ly",
        clean_xml
    ])


    print("jianpu_ly完成")



    # -----------------------
    # LilyPond PDF
    # -----------------------

    run_cmd([
        "lilypond",
        "-o",
        os.path.join(job_dir,"jianpu"),
        ly_path
    ])


    pdf = os.path.join(
        job_dir,
        "jianpu.pdf"
    )


    if not os.path.exists(pdf):

        return JSONResponse(
            {
                "error":"PDF產生失敗",
                "folder":job_dir
            }
        )


    return FileResponse(
        pdf,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )