import os
import uuid
import subprocess
import shutil

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse


app = FastAPI()


@app.get("/")
def home():
    return {
        "status": "JianpuTool running",
        "version": "V21.2.1"
    }


@app.post("/upload")
async def upload(file: UploadFile = File(...)):

    work_dir = os.path.join(
        "outputs",
        str(uuid.uuid4())
    )

    os.makedirs(work_dir, exist_ok=True)


    print("================")
    print("收到:")
    print(file.filename)
    print("================")


    # =====================
    # MP3
    # =====================

    mp3_file = os.path.join(
        work_dir,
        file.filename
    )


    with open(mp3_file,"wb") as f:
        shutil.copyfileobj(
            file.file,
            f
        )

    print("MP3保存完成")


    # =====================
    # BasicPitch
    # =====================

    print("開始 BasicPitch")


    melody_mid = os.path.join(
        work_dir,
        "melody.mid"
    )


    basic_pitch = os.path.join(
        os.path.dirname(__file__),
        "basic_pitch_convert.py"
    )


    result = subprocess.run(
        [
            "python",
            basic_pitch,
            mp3_file,
            melody_mid
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )


    print(result.stdout)


    if not os.path.exists(melody_mid):
        return {
            "error":"BasicPitch failed",
            "log":result.stdout
        }



    # =====================
    # MIDI Quantize
    # =====================

    print("開始 MIDI Quantize")


    clean_mid = os.path.join(
        work_dir,
        "melody_clean.mid"
    )


    subprocess.run(
        [
            "python",
            "midi_quantize.py",
            melody_mid,
            clean_mid
        ]
    )



    # =====================
    # MIDI -> MusicXML
    # =====================

    print("MIDI轉MusicXML")


    input_xml = os.path.join(
        work_dir,
        "input.musicxml"
    )


    subprocess.run(
        [
            "python",
            "midi_to_musicxml.py",
            clean_mid,
            input_xml
        ]
    )



    # =====================
    # Clean MusicXML V21.2
    # =====================

    print("清理 MusicXML")


    clean_xml = os.path.join(
        work_dir,
        "score_clean.musicxml"
    )


    subprocess.run(
        [
            "python",
            "clean_musicxml.py",
            input_xml,
            clean_xml
        ]
    )


    if not os.path.exists(clean_xml):
        return {
            "error":"clean_musicxml failed"
        }



    # =====================
    # Validator V21.2
    # =====================

    print("MusicXML Validator V21.2")


    validator_xml = os.path.join(
        work_dir,
        "jianpu.musicxml"
    )


    from validator_v212 import fix_jianpu_xml


    fix_jianpu_xml(
        clean_xml,
        validator_xml
    )



    # =====================
    # jianpu_ly
    # =====================

    print("產生簡譜")


    ly_file = os.path.join(
        work_dir,
        "jianpu.ly"
    )


    with open(
        ly_file,
        "w",
        encoding="utf-8"
    ) as f:

        subprocess.run(
            [
                "python",
                "-m",
                "jianpu_ly",
                validator_xml
            ],
            stdout=f,
            stderr=subprocess.STDOUT
        )



    # =====================
    # LilyPond PDF
    # =====================

    print("產生PDF")


    subprocess.run(
        [
            "lilypond",
            "-o",
            os.path.join(work_dir,"jianpu"),
            ly_file
        ]
    )


    pdf_file=os.path.join(
        work_dir,
        "jianpu.pdf"
    )


    if os.path.exists(pdf_file):

        return FileResponse(
            pdf_file,
            media_type="application/pdf",
            filename="jianpu.pdf"
        )


    return {
        "status":"完成流程",
        "folder":work_dir
    }