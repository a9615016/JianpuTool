import os
import uuid
import subprocess

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse


app = FastAPI(
    title="JianpuTool"
)


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "outputs"
)


os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)



def run_command(cmd):

    print("執行:")
    print(" ".join(cmd))


    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )


    print(result.stdout)


    if result.returncode != 0:

        raise Exception(
            result.stdout
        )


    return result.stdout




@app.get("/")
def home():

    return HTMLResponse(
        """
        <html>

        <head>
        <title>JianpuTool</title>
        </head>


        <body>

        <h1>
        JianpuTool 簡譜產生器
        </h1>


        <h3>
        MIDI → 簡譜 PDF
        </h3>


        <form action="/midi"
        method="post"
        enctype="multipart/form-data">

        <input type="file"
        name="file">

        <button>
        Convert MIDI
        </button>

        </form>



        <h3>
        MusicXML → 簡譜 PDF
        </h3>


        <form action="/convert"
        method="post"
        enctype="multipart/form-data">

        <input type="file"
        name="file">

        <button>
        Convert MusicXML
        </button>

        </form>


        </body>

        </html>
        """
    )





@app.post("/convert")
async def convert(
    file: UploadFile = File(...)
):


    job = str(uuid.uuid4())


    work = os.path.join(
        OUTPUT_DIR,
        job
    )


    os.makedirs(work)



    input_xml = os.path.join(
        work,
        file.filename
    )


    with open(
        input_xml,
        "wb"
    ) as f:

        f.write(
            await file.read()
        )



    clean_xml = os.path.join(
        work,
        "clean.musicxml"
    )



    print("開始 MusicXML 清理")


    run_command(
        [
            "python",
            "clean_musicxml.py",
            input_xml,
            clean_xml
        ]
    )



    ly_file = os.path.join(
        work,
        "jianpu.ly"
    )



    print("開始 jianpu_ly")


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
                clean_xml
            ],
            stdout=f,
            stderr=subprocess.STDOUT
        )



    print("開始 LilyPond")


    run_command(
        [
            "lilypond",
            "-o",
            work,
            ly_file
        ]
    )



    pdf = os.path.join(
        work,
        "jianpu.pdf"
    )


    if not os.path.exists(pdf):

        raise Exception(
            "PDF產生失敗"
        )


    return FileResponse(
        pdf,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )






@app.post("/midi")
async def midi_convert(
    file: UploadFile = File(...)
):


    job = str(uuid.uuid4())


    work = os.path.join(
        OUTPUT_DIR,
        job
    )


    os.makedirs(work)



    # 原始 MIDI

    midi = os.path.join(
        work,
        file.filename
    )


    with open(
        midi,
        "wb"
    ) as f:

        f.write(
            await file.read()
        )



    # =====================
    # MIDI → Melody MIDI
    # =====================

    print(
        "開始抽取主旋律"
    )


    melody_mid = os.path.join(
        work,
        "melody_clean.mid"
    )


    run_command(
        [
            "python",
            "melody_extractor_v2.py",
            midi,
            melody_mid
        ]
    )



    # =====================
    # Melody MIDI → MusicXML
    # =====================

    print(
        "開始 MIDI → MusicXML"
    )


    musicxml = os.path.join(
        work,
        "input.musicxml"
    )



    run_command(
        [
            "python",
            "midi_to_musicxml.py",
            melody_mid,
            musicxml
        ]
    )



    # =====================
    # Clean MusicXML
    # =====================

    clean_xml = os.path.join(
        work,
        "clean.musicxml"
    )


    print(
        "開始 MusicXML 清理"
    )


    run_command(
        [
            "python",
            "clean_musicxml.py",
            musicxml,
            clean_xml
        ]
    )



    # =====================
    # MusicXML → Jianpu
    # =====================

    ly_file = os.path.join(
        work,
        "jianpu.ly"
    )


    print(
        "開始 jianpu_ly"
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
                clean_xml
            ],
            stdout=f,
            stderr=subprocess.STDOUT
        )



    # =====================
    # LilyPond PDF
    # =====================

    print(
        "開始 LilyPond"
    )


    run_command(
        [
            "lilypond",
            "-o",
            work,
            ly_file
        ]
    )



    pdf = os.path.join(
        work,
        "jianpu.pdf"
    )



    if not os.path.exists(pdf):

        raise Exception(
            "PDF產生失敗"
        )



    return FileResponse(
        pdf,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )