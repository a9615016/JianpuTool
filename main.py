print("========== MAIN.PY VERSION TEST 20260727 ==========")
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
import os
import uuid
import subprocess
from lxml import etree


app = FastAPI()


BASE_DIR = "/app/outputs"

os.makedirs(
    BASE_DIR,
    exist_ok=True
)


print("JianpuTool DEBUG MAIN VERSION 20260727")


@app.get("/")
def home():

    return HTMLResponse(
        """
        <h2>JianpuTool</h2>

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



# ===================================
# jianpu_ly 前 MusicXML duration debug
# ===================================

def debug_duration(xml_file):

    print("==============================")
    print("RAW DURATION CHECK")
    print(xml_file)
    print("==============================")


    try:

        tree = etree.parse(xml_file)

    except Exception as e:

        print(
            "XML READ ERROR",
            e
        )

        return



    notes = tree.findall(
        ".//note"
    )


    pos = 0


    for i, note in enumerate(notes):

        dur = note.find(
            "duration"
        )


        if dur is None:
            continue


        d = int(
            dur.text
        )


        # 顯示第4小節附近
        if 45 <= pos <= 80:

            pitch = note.find(
                "pitch"
            )


            if pitch is not None:

                step = pitch.find(
                    "step"
                )

                octave = pitch.find(
                    "octave"
                )

                name = (
                    step.text
                    +
                    octave.text
                )

            else:

                name = "REST"



            print(
                "NOTE",
                i,
                "pitch=",
                name,
                "pos=",
                pos,
                "duration=",
                d,
                "end=",
                pos+d
            )


        pos += d



    print(
        "TOTAL TICKS:",
        pos
    )

    print("==============================")





@app.post("/upload")
async def upload(
    file: UploadFile = File(...)
):


    uid = str(
        uuid.uuid4()
    )


    workdir = os.path.join(
        BASE_DIR,
        uid
    )


    os.makedirs(
        workdir,
        exist_ok=True
    )


    input_file = os.path.join(
        workdir,
        file.filename
    )


    with open(
        input_file,
        "wb"
    ) as f:

        f.write(
            await file.read()
        )


    print("================")
    print("收到:")
    print(file.filename)
    print("================")



    # =========================
    # clean musicxml
    # =========================


    clean_xml = os.path.join(
        workdir,
        "clean.musicxml"
    )


    print(
        "開始 MusicXML 清理"
    )


    result = subprocess.run(
        [
            "python",
            "clean_musicxml.py",
            input_file,
            clean_xml
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )


    print(
        result.stdout
    )



    if result.returncode != 0:

        return {
            "error":
            result.stdout
        }



    print(
        "清理完成"
    )


    print(
        "CHECK jianpu input:"
    )

    print(
        clean_xml
    )



    # =========================
    # NEW DEBUG
    # =========================

    debug_duration(
        clean_xml
    )



    # =========================
    # jianpu_ly
    # =========================


    print(
        "開始 jianpu_ly"
    )


    print(
        "RUN:",
        "python -m jianpu_ly",
        clean_xml
    )


    ly_result = subprocess.run(

        [
            "python",
            "-m",
            "jianpu_ly",
            clean_xml
        ],

        stdout=subprocess.PIPE,

        stderr=subprocess.STDOUT,

        text=True

    )


    print(
        ly_result.stdout
    )


    if ly_result.returncode != 0:

        return {

            "error":
            ly_result.stdout

        }



    ly_file = os.path.join(
        workdir,
        "output.ly"
    )


    with open(
        ly_file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            ly_result.stdout
        )



    return {

        "status":
        "ok",

        "folder":
        workdir

    }