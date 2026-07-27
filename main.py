import os
import uuid
import subprocess

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse


app = FastAPI()


OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)



@app.get("/")
def home():

    return HTMLResponse("""
    <html>
    <body>

    <h2>JianpuTool 簡譜產生器</h2>

    <form action="/upload"
          method="post"
          enctype="multipart/form-data">

        <input type="file" name="file">

        <button type="submit">
        上傳轉換
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

    os.makedirs(work_dir, exist_ok=True)


    print("====================")
    print("開始任務:", job_id)
    print("收到:", file.filename)
    print("====================")



    # =====================
    # 1. 保存 MP3
    # =====================

    input_audio = os.path.join(
        work_dir,
        file.filename
    )


    with open(input_audio, "wb") as f:
        f.write(await file.read())


    print("MP3保存完成")
    print(input_audio)



    # =====================
    # 2. BasicPitch
    # =====================

    print("開始 BasicPitch")


    midi_file = os.path.join(
        work_dir,
        "melody.mid"
    )


    result = subprocess.run(
        [
            "python",
            "basicpitch_convert.py",
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
            "error":"BasicPitch失敗",
            "log":result.stdout
        }



    print("MIDI完成")



    # =====================
    # 3. MIDI → MusicXML
    # =====================

    print("開始 MIDI轉MusicXML")


    musicxml = os.path.join(
        work_dir,
        "input.musicxml"
    )


    result = subprocess.run(
        [
            "python",
            "midi_to_musicxml.py",
            midi_file,
            musicxml
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )


    print(result.stdout)


    if result.returncode != 0:

        return {
            "error":"MusicXML失敗",
            "log":result.stdout
        }



    print("MusicXML完成")



    # =====================
    # 4. 清理 MusicXML
    # =====================

    print("開始清理 MusicXML")


    clean_xml = os.path.join(
        work_dir,
        "clean.musicxml"
    )


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



    # =====================
    # 5. jianpu_ly
    # =====================

    print("開始 jianpu_ly")


    ly_file = os.path.join(
        work_dir,
        "jianpu.ly"
    )


    with open(
        ly_file,
        "w",
        encoding="utf-8"
    ) as f:


        result = subprocess.run(
            [
                "python",
                "-m",
                "jianpu_ly",
                clean_xml
            ],
            stdout=f,
            stderr=subprocess.STDOUT,
            text=True
        )


    print(
        "jianpu_ly return:",
        result.returncode
    )



    if result.returncode != 0:

        return {
            "error":"jianpu_ly失敗"
        }



    print("LY完成:", ly_file)



    # =====================
    # 6. LilyPond
    # =====================

    print("開始 LilyPond")


    result = subprocess.run(
        [
            "lilypond",
            "-o",
            "jianpu",
            "jianpu.ly"
        ],

        # ★重要修正
        cwd=work_dir,

        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )


    print(result.stdout)


    print(
        "LilyPond return:",
        result.returncode
    )



    if result.returncode != 0:

        return {
            "error":"LilyPond失敗",
            "log":result.stdout
        }



    # =====================
    # 7. 回傳 PDF
    # =====================

    pdf_file = os.path.join(
        work_dir,
        "jianpu.pdf"
    )


    if not os.path.exists(pdf_file):

        return {
            "error":"PDF不存在",
            "folder":work_dir
        }



    print("完成 PDF:")
    print(pdf_file)



    return FileResponse(
        pdf_file,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )