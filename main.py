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
        "version": "V22"
    }



def run_cmd(cmd):

    print("RUN:")
    print(" ".join(cmd))

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    print(result.stdout)

    return result



@app.post("/upload")
async def upload(file: UploadFile = File(...)):

    work_dir = os.path.join(
        "outputs",
        str(uuid.uuid4())
    )

    # 修正 exist_ok
    os.makedirs(
        work_dir,
        exist_ok=True
    )


    input_audio = os.path.join(
        work_dir,
        file.filename
    )


    with open(input_audio,"wb") as f:
        f.write(await file.read())


    print("================")
    print("收到:")
    print(file.filename)
    print("================")



    # =====================
    # BasicPitch
    # =====================

    midi_file = os.path.join(
        work_dir,
        "melody.mid"
    )


    print("開始 BasicPitch")


    r = run_cmd([
        "python",
        "basic_pitch_convert.py",
        input_audio,
        midi_file
    ])


    if r.returncode != 0:
        return {
            "error":"BasicPitch failed",
            "log":r.stdout
        }


    if not os.path.exists(midi_file):
        return {
            "error":"MIDI not created"
        }



    # =====================
    # Quantize
    # =====================

    clean_midi = os.path.join(
        work_dir,
        "melody_clean.mid"
    )


    print("開始 MIDI Quantize")


    r = run_cmd([
        "python",
        "midi_quantize.py",
        midi_file,
        clean_midi
    ])


    if r.returncode != 0:
        return {
            "error":"quantize failed",
            "log":r.stdout
        }



    # =====================
    # MIDI -> MusicXML
    # =====================

    musicxml = os.path.join(
        work_dir,
        "input.musicxml"
    )


    print("MIDI轉MusicXML")


    r = run_cmd([
        "python",
        "midi_to_musicxml.py",
        clean_midi,
        musicxml
    ])


    if r.returncode != 0:
        return {
            "error":"musicxml failed",
            "log":r.stdout
        }



    # =====================
    # Clean MusicXML
    # =====================

    clean_xml = os.path.join(
        work_dir,
        "clean.musicxml"
    )


    print("清理 MusicXML")


    r = run_cmd([
        "python",
        "clean_musicxml.py",
        musicxml,
        clean_xml
    ])


    if r.returncode != 0:
        return {
            "error":"clean_musicxml failed",
            "log":r.stdout
        }



    if not os.path.exists(clean_xml):
        return {
            "error":"clean xml missing"
        }



    # =====================
    # Jianpu LY
    # =====================

    ly_file = os.path.join(
        work_dir,
        "jianpu.ly"
    )


    print("產生簡譜")


    with open(
        ly_file,
        "w",
        encoding="utf-8"
    ) as f:


        r = subprocess.run(
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


    if r.returncode != 0:
        return {
            "error":"jianpu_ly failed",
            "log":r.stderr
        }


    if not os.path.exists(ly_file):
        return {
            "error":"jianpu.ly not created"
        }


    print("jianpu.ly created:")
    print(ly_file)



    # =====================
    # LilyPond
    # =====================

    print("開始 LilyPond")


    r = run_cmd([
        "lilypond",
        "-o",
        work_dir,
        ly_file
    ])


    pdf_file = os.path.join(
        work_dir,
        "jianpu.pdf"
    )


    print("CHECK PDF:")
    print(pdf_file)


    if not os.path.exists(pdf_file):

        return {
            "error":"PDF failed",
            "log":r.stdout
        }


    print("PDF SUCCESS")



    return FileResponse(
        pdf_file,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )