import os
import uuid
import shutil
import subprocess

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse


app = FastAPI()


BASE_DIR = "/app"

OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)



@app.get("/")
def home():

    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
    <title>JianpuTool</title>
    </head>

    <body>

    <h2>AI 簡譜產生器</h2>

    <form action="/upload" method="post" enctype="multipart/form-data">

    <input type="file" name="file">

    <button type="submit">
    轉換簡譜 PDF
    </button>

    </form>

    </body>
    </html>
    """)




@app.post("/upload")
async def upload(file: UploadFile = File(...)):


    job_id = str(uuid.uuid4())

    work_dir = os.path.join(
        OUTPUT_DIR,
        job_id
    )

    os.makedirs(work_dir)


    print("================")
    print("收到:")
    print(file.filename)
    print("================")


    # =========================
    # MP3保存
    # =========================

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



    # =========================
    # BasicPitch
    # =========================

    print("開始 BasicPitch")


    midi_file = os.path.join(
        work_dir,
        "melody.mid"
    )


    result = subprocess.run(
        [
            "python",
            "basicpitch_convert.py",
            mp3_file,
            midi_file
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )


    print(result.stdout)



    # =========================
    # MIDI Quantize
    # =========================


    print("開始 MIDI Quantize")


    clean_mid = os.path.join(
        work_dir,
        "melody_clean.mid"
    )


    subprocess.run(
        [
            "python",
            "midi_quantize.py",
            midi_file,
            clean_mid
        ]
    )


    print("MIDI Quantize完成")



    # =========================
    # MIDI → MusicXML
    # =========================


    print("MIDI轉MusicXML")


    musicxml = os.path.join(
        work_dir,
        "input.musicxml"
    )


    subprocess.run(
        [
            "python",
            "midi_to_musicxml.py",
            clean_mid,
            musicxml
        ]
    )


    print(
        musicxml
    )



    # =========================
    # CLEAN V21.2
    # =========================


    print("清理 MusicXML")


    clean_xml = os.path.join(
        work_dir,
        "Jainpu.musicxml"
    )


    subprocess.run(
        [
            "python",
            "clean_musicxml.py",
            musicxml,
            clean_xml
        ]
    )


    print("V21.2 CLEAN完成")



    # =========================
    # V21.2 FINAL VALIDATOR
    # =========================


    print("MusicXML Validator V21.2")


    final_xml = os.path.join(
        work_dir,
        "final.musicxml"
    )


    from validator_v212 import fix_jianpu_xml


    fix_jianpu_xml(
        clean_xml,
        final_xml
    )


    print(
        "validator完成:",
        final_xml
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
            final_xml
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

        f.write(result.stdout)



    # =========================
    # LilyPond PDF
    # =========================


    print("開始 LilyPond")


    subprocess.run(
        [
            "lilypond",
            "-o",
            os.path.join(work_dir,"output"),
            ly_file
        ]
    )


    pdf_file=os.path.join(
        work_dir,
        "output.pdf"
    )


    if os.path.exists(pdf_file):

        print("PDF完成")

        return FileResponse(
            pdf_file,
            media_type="application/pdf",
            filename="jianpu.pdf"
        )


    else:

        return {
            "error":"PDF產生失敗",
            "folder":work_dir
        }