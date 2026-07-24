from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse
import subprocess
import uuid
import os
import glob
import music21


app = FastAPI()


# Render Linux
LILYPOND = "lilypond"


@app.get("/")
def home():

    return HTMLResponse(
        """
        <h2>🎵 JianpuTool MIDI → 簡譜</h2>

        <form action="/convert" method="post" enctype="multipart/form-data">

        <input type="file" name="file">

        <button type="submit">
        產生簡譜 PDF
        </button>

        </form>
        """
    )


@app.get("/status")
def status():

    return {
        "status":"JianpuTool running",
        "api":[
            "/convert",
            "/midi"
        ]
    }



# ==========================
# MusicXML → Jianpu PDF
# ==========================

def musicxml_to_pdf(musicxml_file, work_dir):


    print("開始 MusicXML -> jianpu")
    print("輸入:", musicxml_file)



    # 先 clean
    clean_file = os.path.join(
        work_dir,
        "clean.musicxml"
    )


    result = subprocess.run(
        [
            "python",
            "clean_musicxml.py",
            musicxml_file,
            clean_file
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )


    if result.returncode != 0:

        return None, result.stderr



    print("clean完成")



    ly_file = os.path.join(
        work_dir,
        "input.ly"
    )



    # jianpu_ly
    result = subprocess.run(
        [
            "python",
            "-m",
            "jianpu_ly",
            clean_file
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )


    print(
        "jianpu_ly:",
        result.returncode
    )



    if result.returncode != 0:

        return None, result.stderr



    ly_text = result.stdout



    # ==========================
    # 修正 jianpu_ly octave
    # ==========================

    ly_text = ly_text.replace(
        "1,1",
        "1"
    )

    ly_text = ly_text.replace(
        "2,2",
        "2"
    )

    ly_text = ly_text.replace(
        "3,3",
        "3"
    )

    ly_text = ly_text.replace(
        "4,4",
        "4"
    )

    ly_text = ly_text.replace(
        "5,5",
        "5"
    )

    ly_text = ly_text.replace(
        "6,6",
        "6"
    )

    ly_text = ly_text.replace(
        "7,7",
        "7"
    )



    with open(
        ly_file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(ly_text)



    # LilyPond PDF

    result = subprocess.run(
        [
            LILYPOND,
            "input.ly"
        ],
        cwd=work_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )


    if result.returncode != 0:

        return None, result.stdout



    pdf_files = glob.glob(
        os.path.join(
            work_dir,
            "*.pdf"
        )
    )


    if not pdf_files:

        return None,"PDF not found"



    return pdf_files[0],None





# ==========================
# MusicXML upload
# ==========================

@app.post("/convert")
async def convert(
    file: UploadFile = File(...)
):


    job_id = str(uuid.uuid4())


    work_dir = os.path.join(
        "outputs",
        job_id
    )


    os.makedirs(
        work_dir,
        exist_ok=True
    )



    musicxml_file = os.path.join(
        work_dir,
        "input.musicxml"
    )



    with open(
        musicxml_file,
        "wb"
    ) as f:

        f.write(
            await file.read()
        )



    pdf,error = musicxml_to_pdf(
        musicxml_file,
        work_dir
    )



    if error:

        return {
            "error":error
        }



    return FileResponse(
        pdf,
        filename="jianpu.pdf",
        media_type="application/pdf"
    )





# ==========================
# MIDI upload
# ==========================

@app.post("/midi")
async def midi_convert(
    file: UploadFile = File(...)
):


    job_id=str(uuid.uuid4())


    work_dir=os.path.join(
        "outputs",
        job_id
    )


    os.makedirs(
        work_dir,
        exist_ok=True
    )



    midi_file=os.path.join(
        work_dir,
        "input.mid"
    )


    musicxml_file=os.path.join(
        work_dir,
        "input.musicxml"
    )



    with open(
        midi_file,
        "wb"
    ) as f:

        f.write(
            await file.read()
        )



    try:

        score = music21.converter.parse(
            midi_file
        )


        score.write(
            "musicxml",
            fp=musicxml_file
        )


    except Exception as e:

        return {
            "error":"MIDI convert failed",
            "detail":str(e)
        }



    pdf,error = musicxml_to_pdf(
        musicxml_file,
        work_dir
    )



    if error:

        return {
            "error":error
        }



    return FileResponse(
        pdf,
        filename="jianpu.pdf",
        media_type="application/pdf"
    )