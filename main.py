from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse
import os
import subprocess
import uuid


app = FastAPI(title="JianpuTool")


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

os.makedirs(OUTPUT_DIR, exist_ok=True)


LILYPOND = r"C:\lilypond-2.26.0\bin\lilypond.exe"


# 支援格式
SUPPORTED = [
    ".mp3",
    ".wav",
    ".mid",
    ".midi"
]


@app.get("/")
def home():

    return HTMLResponse("""
    <html>
    <body>

    <h2>JianpuTool</h2>

    <p>
    支援 MP3 / WAV / MIDI
    </p>

    <form action="/upload"
    method="post"
    enctype="multipart/form-data">

    <input 
    type="file" 
    name="file"
    accept=".mp3,.wav,.mid,.midi">

    <button>
    Convert
    </button>

    </form>

    </body>
    </html>
    """)



@app.post("/upload")
async def upload(file: UploadFile = File(...)):


    ext = os.path.splitext(
        file.filename
    )[1].lower()


    if ext not in SUPPORTED:

        raise Exception(
            "只支援 MP3 WAV MIDI"
        )


    job = str(uuid.uuid4())


    workdir = os.path.join(
        OUTPUT_DIR,
        job
    )

    os.makedirs(
        workdir,
        exist_ok=True
    )


    # 儲存檔案

    input_file = os.path.join(
        workdir,
        file.filename
    )


    with open(input_file,"wb") as f:

        f.write(
            await file.read()
        )


    print("INPUT:",input_file)



    # ==========================
    # WAV / MP3 -> MIDI
    # ==========================

    if ext in [".mp3",".wav"]:


        midi_output = os.path.join(
            workdir,
            "input.mid"
        )


        subprocess.run(
            [
                "python",
                "basicpitch_convert.py",
                input_file,
                midi_output
            ],
            check=True
        )


    # ==========================
    # MIDI直接使用
    # ==========================

    else:

        midi_output = input_file



    print(
        "MIDI:",
        midi_output
    )



    # ==========================
    # MIDI -> MusicXML
    # ==========================


    musicxml = os.path.join(
        workdir,
        "input.musicxml"
    )


    subprocess.run(
        [
            "python",
            "midi_to_musicxml_clean.py",
            midi_output,
            musicxml
        ],
        check=True
    )



    # ==========================
    # Quantize
    # ==========================


    final_xml = os.path.join(
        workdir,
        "final.musicxml"
    )


    subprocess.run(
        [
            "python",
            "final_quantize.py",
            musicxml,
            final_xml
        ],
        check=True
    )



    # ==========================
    # MusicXML -> Jianpu
    # ==========================


    ly_file = os.path.join(
        workdir,
        "jianpu.ly"
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
                final_xml
            ],
            stdout=f,
            check=True
        )



    # ==========================
    # LilyPond PDF
    # ==========================


    subprocess.run(
        [
            LILYPOND,
            ly_file
        ],
        cwd=workdir,
        check=True
    )



    pdf = os.path.join(
        workdir,
        "jianpu.pdf"
    )


    if not os.path.exists(pdf):

        raise Exception(
            "PDF失敗"
        )


    return FileResponse(
        pdf,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )