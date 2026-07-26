import os
import uuid
import subprocess
import shutil

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse


app = FastAPI()


BASE_DIR = "/app"
OUTPUT_DIR = "/app/outputs"

os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.get("/")
def home():
    return HTMLResponse("""
    <h2>JianpuTool</h2>

    <form action="/upload" method="post" enctype="multipart/form-data">

    <input type="file" name="file">

    <button type="submit">
    Convert
    </button>

    </form>
    """)



@app.post("/upload")
async def upload(file: UploadFile = File(...)):

    work_id = str(uuid.uuid4())
    work_dir = os.path.join(
        OUTPUT_DIR,
        work_id
    )

    os.makedirs(work_dir)


    print("================")
    print("收到:")
    print(file.filename)
    print("================")


    # =====================
    # Save MP3
    # =====================

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


    # =====================
    # BasicPitch
    # =====================

    print("開始 BasicPitch")


    midi = os.path.join(
        work_dir,
        "melody.mid"
    )


    result = subprocess.run(
        [
            "python",
            "basicpitch_convert.py",
            mp3,
            midi
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )


    print(result.stdout)


    if not os.path.exists(midi):
        return {
            "error":"BasicPitch failed",
            "log":result.stdout
        }



    # =====================
    # MIDI -> MusicXML
    # =====================

    print("MIDI轉MusicXML")


    xml = os.path.join(
        work_dir,
        "score.musicxml"
    )


    result = subprocess.run(
        [
            "python",
            "midi_to_musicxml.py",
            midi,
            xml
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )


    print(result.stdout)



    # =====================
    # Clean MusicXML V13
    # =====================

    print("清理 MusicXML")


    clean_xml = os.path.join(
        work_dir,
        "score_clean.musicxml"
    )


    result = subprocess.run(
        [
            "python",
            "clean_musicxml.py",
            xml,
            clean_xml
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )


    print(result.stdout)



    # =====================
    # jianpu_ly
    # =====================

    print("產生簡譜")


    ly_file = os.path.join(
        work_dir,
        "jianpu.ly"
    )


    print("執行 jianpu_ly")


    result = subprocess.run(
        [
            "python",
            "-m",
            "jianpu_ly",
            clean_xml
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )


    print("================")
    print("jianpu_ly stderr:")
    print(result.stderr)


    if result.returncode != 0:
        return {
            "error":"jianpu_ly failed",
            "log":result.stderr
        }


    # 只寫 stdout
    ly_content = result.stdout


    # 移除前面非 LilyPond 內容
    start = ly_content.find("OctavesAfter")f.write(

    if start != -1:
        ly_content = ly_content[start:]


    with open(
    ly_file,
    "w",
    encoding="utf-8"
    ) as f:
       f.write(ly_content)


    print("jianpu.ly完成")
    with open(
    ly_file,
    encoding="utf-8"
    ) as f:
    print(f.read(100))


    # DEBUG 第一行
    with open(
        ly_file,
        encoding="utf-8"
    ) as f:

        print(
            f.read(200)
        )



    # =====================
    # LilyPond PDF
    # =====================


    print("LilyPond PDF")


    result = subprocess.run(
        [
            "lilypond",
            "-o",
            os.path.join(
                work_dir,
                "jianpu"
            ),
            ly_file
        ],
        cwd=work_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )


    print(result.stdout)



    pdf = os.path.join(
        work_dir,
        "jianpu.pdf"
    )


    if not os.path.exists(pdf):

        return {
            "error":"PDF failed",
            "log":result.stdout
        }


    return FileResponse(
        pdf,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )