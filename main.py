import os
import uuid
import subprocess
import shutil

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse

from patch_jianpu import patch_jianpu


app = FastAPI(
    title="JianpuTool"
)


# 啟動時 patch jianpu_ly
patch_jianpu()


BASE = "/app/outputs"


os.makedirs(BASE, exist_ok=True)


@app.get("/")
def home():

    return HTMLResponse(
"""
<html>
<head>
<title>JianpuTool</title>
</head>

<body>

<h2>JianpuTool</h2>

<p>
MP3 → MIDI → MusicXML → 簡譜 PDF
</p>


<form action="/upload"
method="post"
enctype="multipart/form-data">

<input type="file"
name="file"
accept=".mp3,.wav">


<button type="submit">
開始轉換
</button>

</form>

</body>
</html>
"""
)



@app.post("/upload")
async def upload(
    file: UploadFile = File(...)
):


    job = str(uuid.uuid4())

    outdir = os.path.join(
        BASE,
        job
    )

    os.makedirs(
        outdir,
        exist_ok=True
    )


    print("====================")
    print("開始任務:", job)
    print("收到:", file.filename)


    # MP3 保存

    input_audio = os.path.join(
        outdir,
        file.filename
    )


    with open(
        input_audio,
        "wb"
    ) as f:

        shutil.copyfileobj(
            file.file,
            f
        )


    print("MP3保存完成")


    midi = os.path.join(
        outdir,
        "melody.mid"
    )


    # BasicPitch

    subprocess.run(
        [
            "python",
            "basicpitch_convert.py",
            input_audio,
            midi
        ],
        check=True
    )


    print("MIDI完成")


    musicxml = os.path.join(
        outdir,
        "input.musicxml"
    )


    # MIDI -> MusicXML

    subprocess.run(
        [
            "python",
            "midi_to_musicxml.py",
            midi,
            musicxml
        ],
        check=True
    )


    print("MusicXML完成")


    clean = os.path.join(
        outdir,
        "clean.musicxml"
    )


    # Clean MusicXML

    subprocess.run(
        [
            "python",
            "clean_musicxml.py",
            musicxml,
            clean
        ],
        check=True
    )


    print("清理完成")


    print("CHECK jianpu input:")
    print(clean)



    # jianpu_ly

    ly_file = os.path.join(
        outdir,
        "output.ly"
    )


    with open(
        ly_file,
        "w",
        encoding="utf-8"
    ) as f:


        subprocess.run(
            [
                "python",
                "-m",
                "jianpu_ly",
                clean
            ],
            stdout=f,
            stderr=subprocess.STDOUT,
            check=True
        )


    print("jianpu ly 完成")


    # LilyPond PDF

    subprocess.run(
        [
            "lilypond",
            ly_file
        ],
        cwd=outdir,
        check=True
    )


    pdf = os.path.join(
        outdir,
        "output.pdf"
    )


    print("PDF完成")
    print(pdf)


    return FileResponse(
        pdf,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )