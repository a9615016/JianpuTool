print("========== V91 LOADED ==========")
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse
import os
import uuid
import shutil
import subprocess


print("========== JianpuTool V91 DIRECT MIDI ==========")


app = FastAPI()


BASE_DIR="/app/outputs"

os.makedirs(BASE_DIR,exist_ok=True)



@app.get("/")
def home():

    return HTMLResponse("""
    <h2>JianpuTool V91</h2>

    MP3/WAV → MIDI → Jianpu PDF

    <form action="/upload"
    method="post"
    enctype="multipart/form-data">

    <input type="file" name="file">

    <button>
    Convert
    </button>

    </form>
    """)



@app.post("/upload")
async def upload(file:UploadFile=File(...)):


    job=str(uuid.uuid4())

    out=os.path.join(BASE_DIR,job)

    os.makedirs(out,exist_ok=True)


    src=os.path.join(out,file.filename)


    with open(src,"wb") as f:
        shutil.copyfileobj(file.file,f)



    print("INPUT:",src)



    midi=os.path.join(out,"melody.mid")


    print("STEP1 AUDIO TO MIDI")


    subprocess.run(
        [
            "python",
            "voice_to_midi.py",
            src,
            midi
        ],
        check=True,
        timeout=300
    )


    print("MIDI OK",midi)



    ly=os.path.join(out,"jianpu.ly")


    print("STEP2 MIDI TO LY")


    subprocess.run(
        [
            "python",
            "midi_to_jianpu_ly.py",
            midi,
            ly
        ],
        check=True,
        timeout=120
    )


    print("LY OK")



    print("STEP3 LILYPOND")


    subprocess.run(
        [
            "lilypond",
            "--pdf",
            ly
        ],
        cwd=out,
        check=True,
        timeout=180
    )



    pdf=ly.replace(".ly",".pdf")


    if not os.path.exists(pdf):
        raise Exception("PDF FAIL")



    print("DONE",pdf)


    return FileResponse(
        pdf,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )