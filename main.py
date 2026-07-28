import os
import uuid
import subprocess

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse


app = FastAPI()


BASE_DIR = "/app"

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "outputs"
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)



def run_cmd(cmd):

    print("RUN:", " ".join(cmd))

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    print(result.stdout)

    if result.returncode != 0:

        raise Exception(
            result.stdout
        )



@app.get("/")
def home():

    return {
        "service":
        "JianpuTool MP3 -> Jianpu PDF",
        "version":
        "v1.0"
    }




@app.post("/upload")
async def upload(
    file: UploadFile = File(...)
):


    task_id = str(
        uuid.uuid4()
    )


    workdir = os.path.join(
        OUTPUT_DIR,
        task_id
    )


    os.makedirs(
        workdir,
        exist_ok=True
    )


    print("====================")
    print("開始任務:", task_id)
    print("收到:", file.filename)



    # =====================
    # save mp3
    # =====================

    mp3_file = os.path.join(
        workdir,
        file.filename
    )


    with open(
        mp3_file,
        "wb"
    ) as f:

        f.write(
            await file.read()
        )


    print("MP3保存完成")



    # =====================
    # BasicPitch
    # =====================

    midi_file = os.path.join(
        workdir,
        "melody.mid"
    )


    run_cmd([
        "python",
        "basicpitch_convert.py",
        mp3_file,
        midi_file
    ])


    print("MIDI完成")



    # =====================
    # CLEAN MIDI
    # =====================

    clean_midi = os.path.join(
        workdir,
        "clean.mid"
    )


    run_cmd([
        "python",
        "clean_midi.py",
        midi_file,
        clean_midi
    ])


    print("clean MIDI完成")



    # =====================
    # MIDI -> MusicXML
    # =====================

    musicxml_file = os.path.join(
        workdir,
        "input.musicxml"
    )


    run_cmd([
        "python",
        "midi_to_musicxml.py",
        clean_midi,
        musicxml_file
    ])


    print("MusicXML完成")



    # =====================
    # CLEAN MUSICXML
    # =====================

    clean_xml = os.path.join(
        workdir,
        "clean.musicxml"
    )


    run_cmd([
        "python",
        "clean_musicxml.py",
        musicxml_file,
        clean_xml
    ])


    print("清理完成")



    # =====================
    # jianpu_ly
    # =====================

    ly_file = os.path.join(
        workdir,
        "jianpu.ly"
    )


    run_cmd([
        "python",
        "-m",
        "jianpu_ly",
        clean_xml
    ])


    print("jianpu完成")



    # jianpu_ly 預設輸出 stdout
    # 若需要寫檔，可以改成自行保存



    # =====================
    # LilyPond
    # =====================

    run_cmd([
        "lilypond",
        ly_file
    ])



    pdf_file = os.path.join(
        workdir,
        "jianpu.pdf"
    )


    if not os.path.exists(pdf_file):

        raise Exception(
            "PDF沒有產生"
        )



    print("====================")
    print("完成")
    print(pdf_file)



    return FileResponse(
        pdf_file,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )