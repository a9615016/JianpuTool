import os
import uuid
import glob
import subprocess

import music21

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse


app = FastAPI()


# ==========================
# LilyPond
# ==========================

LILYPOND = "lilypond"


if os.name == "nt":
    LILYPOND = r"C:\lilypond-2.26.0\bin\lilypond.exe"



# ==========================
# 首頁
# ==========================

@app.get("/", response_class=HTMLResponse)
def home():

    return """

<!DOCTYPE html>

<html lang="zh-TW">

<head>

<meta charset="UTF-8">

<title>JianpuTool</title>

<style>

body{

font-family:Arial;
text-align:center;
background:#f5f5f5;
padding:40px;

}


.box{

background:white;
padding:30px;
border-radius:15px;
max-width:500px;
margin:auto;

}


button{

padding:12px 25px;
font-size:16px;
cursor:pointer;

}


input{

margin:15px;

}

</style>

</head>


<body>


<div class="box">


<h1>🎵 JianpuTool</h1>

<h3>MusicXML → 數字簡譜 PDF</h3>


<form action="/convert"
method="post"
enctype="multipart/form-data">


<input type="file"
name="file"
accept=".musicxml,.xml"
required>


<br>


<button>
產生簡譜 PDF
</button>


</form>



<hr>


<h3>MIDI → 數字簡譜 PDF</h3>


<form action="/midi"
method="post"
enctype="multipart/form-data">


<input type="file"
name="file"
accept=".mid,.midi"
required>


<br>


<button>
MIDI 轉簡譜
</button>


</form>


</div>


</body>

</html>

"""



# ==========================
# MusicXML → PDF
# ==========================

def musicxml_to_pdf(
    musicxml_file,
    work_dir
):


    print(
        "開始 MusicXML 清理",
        flush=True
    )


    clean_file = os.path.join(
        work_dir,
        "clean.musicxml"
    )


    subprocess.run(

        [
            "python",
            "clean_musicxml.py",
            musicxml_file,
            clean_file
        ],

        check=True

    )


    print(
        "清理完成",
        flush=True
    )



    ly_file = os.path.join(
        work_dir,
        "input.ly"
    )



    print(
        "開始 jianpu_ly",
        flush=True
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
                clean_file
            ],

            stdout=f,
            stderr=subprocess.PIPE,
            text=True

        )



    print(
        "jianpu_ly return:",
        result.returncode,
        flush=True
    )



    if result.returncode != 0:

        return None, result.stderr




    print(
        "開始 LilyPond",
        flush=True
    )



    result2 = subprocess.run(

        [
            LILYPOND,
            "input.ly"
        ],

        cwd=work_dir,

        stdout=subprocess.PIPE,

        stderr=subprocess.STDOUT,

        text=True

    )


    print(
        result2.stdout,
        flush=True
    )



    if result2.returncode != 0:

        return None,result2.stdout



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
# MusicXML 上傳
# ==========================

@app.post("/convert")
async def convert(
    file:UploadFile=File(...)
):


    job=str(uuid.uuid4())


    work_dir=os.path.join(
        "outputs",
        job
    )


    os.makedirs(
        work_dir,
        exist_ok=True
    )


    xml=os.path.join(
        work_dir,
        "input.musicxml"
    )



    with open(
        xml,
        "wb"
    ) as f:

        f.write(
            await file.read()
        )



    pdf,error = musicxml_to_pdf(
        xml,
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
# MIDI 上傳
# ==========================

@app.post("/midi")
async def midi_convert(
    file:UploadFile=File(...)
):


    job=str(uuid.uuid4())


    work_dir=os.path.join(
        "outputs",
        job
    )


    os.makedirs(
        work_dir,
        exist_ok=True
    )



    midi=os.path.join(
        work_dir,
        "input.mid"
    )


    xml=os.path.join(
        work_dir,
        "input.musicxml"
    )



    with open(
        midi,
        "wb"
    ) as f:

        f.write(
            await file.read()
        )



    try:


        score = music21.converter.parse(
            midi
        )


        if len(score.parts)>0:

            score=score.parts[0]


        score=score.flatten()


        score.write(
            "musicxml",
            fp=xml
        )


    except Exception as e:

        return {
            "error":str(e)
        }




    pdf,error = musicxml_to_pdf(
        xml,
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