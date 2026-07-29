from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
import os
import uuid
import shutil
import subprocess


app = FastAPI()


OUTPUT_DIR = "/app/outputs"

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)



@app.get("/")
def home():

    return HTMLResponse(
        """
        <h2>JianpuTool 簡譜產生器</h2>

        <form action="/upload"
        method="post"
        enctype="multipart/form-data">

        <input type="file" name="file">

        <button>
        Upload
        </button>

        </form>
        """
    )




@app.post("/upload")
async def upload(
    file: UploadFile = File(...)
):

    job_id = str(uuid.uuid4())

    job_dir = os.path.join(
        OUTPUT_DIR,
        job_id
    )

    os.makedirs(
        job_dir,
        exist_ok=True
    )


    input_file = os.path.join(
        job_dir,
        file.filename
    )


    with open(input_file,"wb") as f:
        shutil.copyfileobj(
            file.file,
            f
        )


    print("INPUT:",input_file)



    # =====================
    # MP3 -> MIDI
    # =====================

    midi_path=os.path.join(
        job_dir,
        "melody.mid"
    )


    subprocess.run(
        [
            "python",
            "basicpitch_convert.py",
            input_file,
            midi_path
        ],
        check=True
    )


    print("MIDI DONE")



    # =====================
    # MIDI -> MusicXML
    # =====================

    raw_xml=os.path.join(
        job_dir,
        "input.musicxml"
    )


    subprocess.run(
        [
            "python",
            "midi_to_musicxml.py",
            midi_path,
            raw_xml
        ],
        check=True
    )


    print("MusicXML DONE")




    # =====================
    # CLEAN MUSICXML v27
    # =====================

    clean_xml=os.path.join(
        job_dir,
        "clean.musicxml"
    )


    subprocess.run(
        [
            "python",
            "JianpuTool/clean_musicxml.py",
            raw_xml,
            clean_xml
        ],
        check=True
    )


    print(
        "CLEAN DONE",
        clean_xml
    )



    if not os.path.exists(clean_xml):

        return JSONResponse(
            {
                "error":
                "clean.musicxml missing"
            }
        )





    # =====================
    # MusicXML -> Jianpu LY
    # =====================


    result=subprocess.run(
        [
            "python",
            "-m",
            "jianpu_ly",
            clean_xml
        ],
        capture_output=True,
        text=True
    )


    print(result.stderr)



    if result.returncode !=0:

        return JSONResponse(
            {
                "error":
                "jianpu_ly failed",
                "detail":
                result.stderr[-1500:]
            }
        )



    ly_file=os.path.join(
        job_dir,
        "jianpu.ly"
    )


    with open(
        ly_file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            result.stdout
        )



    print(
        "LY DONE"
    )




    # =====================
    # LilyPond
    # =====================


    subprocess.run(
        [
            "lilypond",
            "-o",
            os.path.join(
                job_dir,
                "jianpu"
            ),
            ly_file
        ],
        check=True
    )



    pdf=os.path.join(
        job_dir,
        "jianpu.pdf"
    )

c
    if not os.path.exists(pdf):

        return JSONResponse(
            {
                "error":
                "PDF failed"
            }
        )



    print(
        "PDF DONE"
    )


    return FileResponse(
        pdf,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )