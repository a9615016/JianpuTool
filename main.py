import os
import uuid
import shutil
import subprocess

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse


app = FastAPI()


BASE_DIR = "outputs"

os.makedirs(
    BASE_DIR,
    exist_ok=True
)



# ==========================
# 首頁
# ==========================

@app.get("/", response_class=HTMLResponse)
def home():

    return """

<!DOCTYPE html>

<html>

<head>

<meta charset="utf-8">

<title>JianpuTool</title>

</head>


<body>


<h1>
JianpuTool
</h1>


<h2>
MusicXML → 簡譜 PDF
</h2>


<form action="/convert"
method="post"
enctype="multipart/form-data">


<input type="file"
name="file"
accept=".musicxml,.xml">


<br><br>


<button type="submit">

MusicXML 轉簡譜

</button>


</form>



<hr>



<h2>
MIDI → 簡譜 PDF
</h2>



<form action="/midi"
method="post"
enctype="multipart/form-data">


<input type="file"
name="file"
accept=".mid,.midi">


<br><br>


<button type="submit">

MIDI 轉簡譜

</button>


</form>



</body>

</html>

"""



# ==========================
# 共用 PDF產生
# ==========================

def generate_pdf(xml_file, workdir):


    print(
        "開始 clean MusicXML"
    )


    clean_file = os.path.join(
        workdir,
        "clean.musicxml"
    )


    subprocess.run(
        [
            "python",
            "clean_musicxml.py",
            xml_file,
            clean_file
        ],
        check=True
    )



    print(
        "開始 rebuild MusicXML"
    )


    rebuild_file = os.path.join(
        workdir,
        "rebuild.musicxml"
    )


    subprocess.run(
        [
            "python",
            "rebuild_musicxml.py",
            clean_file,
            rebuild_file
        ],
        check=True
    )



    print(
        "開始 jianpu_ly"
    )


    ly_file = os.path.join(
        workdir,
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
                rebuild_file
            ],
            stdout=f,
            stderr=subprocess.PIPE,
            text=True
        )



    print(
        "jianpu_ly:",
        result.returncode
    )



    if result.returncode != 0:

        raise Exception(
            result.stderr
        )



    print(
        "開始 LilyPond"
    )



    subprocess.run(
        [
            "lilypond",
            "-o",
            os.path.join(
                workdir,
                "jianpu"
            ),
            ly_file
        ],
        check=True
    )



    pdf_file = os.path.join(
        workdir,
        "jianpu.pdf"
    )


    return pdf_file





# ==========================
# MusicXML → PDF
# ==========================

@app.post("/convert")
async def convert(
    file: UploadFile = File(...)
):


    job_id = str(uuid.uuid4())


    workdir = os.path.join(
        BASE_DIR,
        job_id
    )


    os.makedirs(
        workdir,
        exist_ok=True
    )



    xml_file = os.path.join(
        workdir,
        "input.musicxml"
    )



    with open(
        xml_file,
        "wb"
    ) as f:

        shutil.copyfileobj(
            file.file,
            f
        )



    print(
        "開始 MusicXML -> Jianpu"
    )


    pdf = generate_pdf(
        xml_file,
        workdir
    )


    return FileResponse(
        pdf,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )





# ==========================
# MIDI → PDF
# ==========================

@app.post("/midi")
async def midi_convert(
    file: UploadFile = File(...)
):


    job_id = str(uuid.uuid4())


    workdir = os.path.join(
        BASE_DIR,
        job_id
    )


    os.makedirs(
        workdir,
        exist_ok=True
    )



    midi_file = os.path.join(
        workdir,
        "input.mid"
    )



    with open(
        midi_file,
        "wb"
    ) as f:


        shutil.copyfileobj(
            file.file,
            f
        )



    print(
        "開始 MIDI -> MusicXML"
    )



    subprocess.run(
        [
            "python",
            "converter.py",
            midi_file
        ],
        check=True
    )



    xml_file = os.path.splitext(
        midi_file
    )[0] + ".musicxml"



    print(
        xml_file
    )



    pdf = generate_pdf(
        xml_file,
        workdir
    )



    return FileResponse(
        pdf,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )




# ==========================
# Status
# ==========================

@app.get("/status")
def status():

    return {

        "status":
        "JianpuTool running",

        "api":
        [
            "/convert",
            "/midi"
        ]

    }