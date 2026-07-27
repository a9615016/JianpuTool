import os
import uuid
import subprocess
import shutil

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse


app = FastAPI(title="JianpuTool")


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.get("/", response_class=HTMLResponse)
def home():

    return """
    <html>
    <head>
    <title>JianpuTool</title>
    </head>

    <body>

    <h2>
    JianpuTool 簡譜產生器
    </h2>

    <p>
    MP3 / WAV → MIDI → MusicXML → 數字簡譜 PDF
    </p>


    <form action="/upload" 
          enctype="multipart/form-data"
          method="post">

        <input type="file" name="file">

        <br><br>

        <button type="submit">
        產生簡譜 PDF
        </button>

    </form>


    </body>
    </html>
    """



@app.post("/upload")
async def upload(file: UploadFile = File(...)):


    job_id = str(uuid.uuid4())

    work_dir = os.path.join(
        OUTPUT_DIR,
        job_id
    )

    os.makedirs(work_dir)



    input_file = os.path.join(
        work_dir,
        file.filename
    )


    # 保存上傳檔案
    with open(input_file, "wb") as f:

        shutil.copyfileobj(
            file.file,
            f
        )



    print("================")
    print("收到:")
    print(file.filename)
    print("================")



    ext = os.path.splitext(file.filename)[1].lower()



    midi_file = os.path.join(
        work_dir,
        "melody.mid"
    )



    # ==========================
    # MP3/WAV → MIDI
    # ==========================

    if ext in [".mp3", ".wav"]:


        print("開始 BasicPitch")


        result = subprocess.run(
            [
                "python",
                "basicpitch_convert.py",
                input_file,
                midi_file
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )


        print(result.stdout)


        if result.returncode != 0:

            return {
                "error":
                result.stdout
            }



    elif ext == ".mid":

        midi_file = input_file


    else:

        return {
            "error":
            "只支援 MP3 WAV MIDI"
        }



    # ==========================
    # MIDI → MusicXML
    # ==========================

    musicxml = os.path.join(
        work_dir,
        "score.musicxml"
    )


    print("MIDI轉MusicXML")


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
            "error":
            result.stdout
        }



    # ==========================
    # MusicXML 清理
    # ==========================

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



    # ==========================
    # MusicXML → Jianpu LY
    # ==========================

    ly_file = os.path.join(
        work_dir,
        "jianpu.ly"
    )


    print("jianpu_ly")


    with open(ly_file, "w", encoding="utf-8") as f:

        subprocess.run(
            [
                "python",
                "-m",
                "jianpu_ly",
                clean_xml
            ],
            stdout=f,
            stderr=subprocess.STDOUT
        )



    # ==========================
    # LilyPond PDF
    # ==========================


    print("LilyPond")


    subprocess.run(
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



    pdf_file = os.path.join(
        work_dir,
        "jianpu.pdf"
    )



    if not os.path.exists(pdf_file):

        return {

            "error":
            "PDF產生失敗",

            "folder":
            work_dir

        }



    return FileResponse(

        pdf_file,

        media_type="application/pdf",

        filename="jianpu.pdf"

    )