import os
import uuid
import subprocess

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse


app = FastAPI()


@app.get("/")
def home():
    return {
        "status": "JianpuTool running",
        "version": "V21.3"
    }


@app.post("/upload")
async def upload(file: UploadFile = File(...)):

    work_dir = os.path.join(
        "outputs",
        str(uuid.uuid4())
    )

    os.makedirs(work_dir, exist_ok=True)


    # =====================
    # 保存 MP3
    # =====================

    input_audio = os.path.join(
        work_dir,
        file.filename
    )

    with open(input_audio, "wb") as f:
        f.write(await file.read())


    print("================")
    print("收到:")
    print(file.filename)
    print("================")
    print("MP3保存完成")


    # =====================
    # BasicPitch
    # =====================

    midi_file = os.path.join(
        work_dir,
        "melody.mid"
    )


    print("開始 BasicPitch")


    result = subprocess.run(
        [
            "python",
            "basic_pitch_convert.py",
            input_audio,
            midi_file
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )


    print(result.stdout)


    if result.returncode != 0:
        return {
            "error": "BasicPitch failed",
            "log": result.stdout
        }


    if not os.path.exists(midi_file):
        return {
            "error": "MIDI not created"
        }


    print("MIDI完成:", midi_file)



    # =====================
    # MIDI Quantize
    # =====================

    clean_midi = os.path.join(
        work_dir,
        "melody_clean.mid"
    )


    print("開始 MIDI Quantize")


    result = subprocess.run(
        [
            "python",
            "midi_quantize.py",
            midi_file,
            clean_midi
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )


    print(result.stdout)


    if result.returncode != 0:
        return {
            "error":"quantize failed",
            "log":result.stdout
        }



    # =====================
    # MIDI → MusicXML
    # =====================

    musicxml = os.path.join(
        work_dir,
        "input.musicxml"
    )


    print("MIDI轉MusicXML")


    result = subprocess.run(
        [
            "python",
            "midi_to_musicxml.py",
            clean_midi,
            musicxml
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )


    print(result.stdout)


    if result.returncode != 0:
        return {
            "error":"musicxml failed",
            "log":result.stdout
        }



    # =====================
    # Clean MusicXML
    # =====================

    clean_xml = os.path.join(
        work_dir,
        "clean.musicxml"
    )


    print("清理 MusicXML")


    result = subprocess.run(
        [
            "python",
            "clean_musicxml.py",
            musicxml,
            clean_xml
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )


    print(result.stdout)


    if result.returncode != 0:
        return {
            "error":"clean_musicxml failed",
            "log":result.stdout
        }



    # =====================
    # Jianpu
    # =====================

    ly_file = os.path.join(
        work_dir,
        "jianpu.ly"
    )


    print("產生簡譜")


    with open(ly_file, "w", encoding="utf-8") as f:

        result = subprocess.run(
            [
                "python",
                "-m",
                "jianpu_ly",
                clean_xml
            ],
            stdout=f,
            stderr=subprocess.PIPE,
            text=True
        )


    if result.returncode != 0:
        return {
            "error":"jianpu_ly failed",
            "log":result.stderr
        }



    # =====================
    # LilyPond PDF
    # =====================

    print("產生PDF")


    result = subprocess.run(
        [
            "lilypond",
            "-o",
            work_dir,
            ly_file
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )


    print(result.stdout)


    pdf_file = os.path.join(
        work_dir,
        "jianpu.pdf"
    )


    if not os.path.exists(pdf_file):
        return {
            "error":"PDF failed",
            "log":result.stdout
        }


    return FileResponse(
        pdf_file,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )