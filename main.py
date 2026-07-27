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


print("========== JianpuTool MAIN DEBUG 20260727 ==========")



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



# ==================================
# jianpu_ly 前 MusicXML duration檢查
# ==================================

def debug_duration(xml_file):

    print("==============================")
    print("JIANPU INPUT DURATION DEBUG")
    print(xml_file)
    print("==============================")


    try:

        tree = etree.parse(xml_file)

    except Exception as e:

        print(
            "XML ERROR:",
            e
        )

        return



    notes = tree.findall(
        ".//note"
    )


    pos = 0


    for i, note in enumerate(notes):


        duration = note.find(
            "duration"
        )


        if duration is None:
            continue


        d = int(
            duration.text
        )


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
                    step.text +
                    octave.text
                )

            else:

                name = "REST"



            print(
                "NOTE",
                i,
                "pitch=",
                name,
                "start=",
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



    # ==============================
    # MusicXML clean
    # ==============================


    clean_xml = os.path.join(
        workdir,
        "clean.musicxml"
    )


    print(
        "開始 MusicXML 清理"
    )


    clean_result = subprocess.run(

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
        clean_result.stdout
    )


    if clean_result.returncode != 0:

        return {

            "error":
            "clean_musicxml失敗",

            "log":
            clean_result.stdout

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



    # ==============================
    # NEW DEBUG
    # ==============================

    debug_duration(
        clean_xml
    )



    # ==============================
    # jianpu_ly
    # ==============================


    print(
        "開始 jianpu_ly"
    )


    cmd = [

        "python",

        "-m",

        "jianpu_ly",

        clean_xml

    ]


    print(
        "RUN:",
        " ".join(cmd)
    )


    result = subprocess.run(

        cmd,

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
            "jianpu_ly失敗",

            "log":
            result.stdout

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
            result.stdout
        )



    return {

        "status":
        "ok",

        "ly":
        ly_file

    }