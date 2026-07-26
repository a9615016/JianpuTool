import os
import uuid
import subprocess
import shutil

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse


app = FastAPI()


BASE_DIR = "/app"
OUTPUT_DIR = "outputs"


os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.get("/")
def home():
    return {
        "status": "JianpuTool running",
        "version": "V21.2.1"
    }



@app.post("/upload")
async def upload(file: UploadFile = File(...)):

    work_id = str(uuid.uuid4())

    work_dir = os.path.join(
        OUTPUT_DIR,
        work_id
    )

    os.makedirs(work_dir, exist_ok=True)


    print("================")
    print("收到:")
    print(file.filename)
    print("================")


    # =========================
    # MP3 SAVE
    # =========================

    mp3 = os.path.join(
        work_dir,
        file.filename
    )


    with open(mp3,"wb") as f:
        shutil.copyfileobj(
            file.file,
            f
        )


    print("MP3保存完成")



    # =========================
    # BasicPitch
    # =========================

    print("開始 BasicPitch")


    midi = os.path.join(
        work_dir,
        "melody.mid"
    )


    result = subprocess.run(
        [
            "python",
            "basic_pitch_convert.py",
            mp3,
            midi
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )


    print(result.stdout)


    if result.returncode != 0:
        return {
            "error":"BasicPitch失敗",
            "log":result.stdout
        }



    print("MIDI完成:",midi)



    # =========================
    # MIDI Quantize
    # =========================


    clean_mid = os.path.join(
        work_dir,
        "melody_clean.mid"
    )


    print("開始 MIDI Quantize")


    subprocess.run(
        [
            "python",
            "midi_quantize.py",
            midi,
            clean_mid
        ]
    )



    print("MIDI Quantize完成")



    # =========================
    # MIDI -> MusicXML
    # =========================


    musicxml = os.path.join(
        work_dir,
        "input.musicxml"
    )


    print("MIDI轉MusicXML")


    subprocess.run(
        [
            "python",
            "midi_to_musicxml.py",
            clean_mid,
            musicxml
        ]
    )


    print(
        "MusicXML:",
        musicxml
    )



    # =========================
    # CLEAN V21.2
    # =========================


    print("清理 MusicXML")


    score_clean = os.path.join(
        work_dir,
        "score_clean.musicxml"
    )


    result = subprocess.run(
        [
            "python",
            "clean_musicxml.py",
            musicxml,
            score_clean
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )


    print(result.stdout)



    if not os.path.exists(score_clean):

        return {
            "error":
            "clean_musicxml沒有產生 score_clean.musicxml"
        }



    print(
        "V21.2 CLEAN完成",
        score_clean
    )



    # =========================
    # VALIDATOR V21.2
    # =========================


    print("MusicXML Validator V21.2")


    validated = os.path.join(
        work_dir,
        "validated.musicxml"
    )


    from validator_v212 import fix_jianpu_xml


    fix_jianpu_xml(
        score_clean,
        validated
    )


    print(
        "Validator完成:",
        validated
    )



    # =========================
    # jianpu_ly
    # =========================


    print("產生簡譜")


    ly_file = os.path.join(
        work_dir,
        "jianpu.ly"
    )


    result = subprocess.run(
        [
            "python",
            "-m",
            "jianpu_ly",
            validated
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )


    print(result.stdout)



    with open(
        ly_file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            result.stdout
        )



    # =========================
    # LilyPond PDF
    # =========================


    print("開始 LilyPond")


    subprocess.run(
        [
            "lilypond",
            "-o",
            work_dir,
            ly_file
        ]
    )


    pdf = os.path.join(
        work_dir,
        "jianpu.pdf"
    )



    if os.path.exists(pdf):

        return FileResponse(
            pdf,
            media_type="application/pdf",
            filename="jianpu.pdf"
        )


    return {
        "status":"完成",
        "folder":work_dir
    }