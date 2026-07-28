# main.py
# JianpuTool v26 DEBUG
# FastAPI
# MusicXML -> clean -> jianpu_ly


from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse

import os
import uuid
import subprocess

from music21 import converter


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
        <h1>JianpuTool 簡譜產生器</h1>

        <p>
        MP3/WAV → MusicXML → Jianpu PDF
        </p>

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



    #
    # 你的原流程
    # MP3 -> MIDI -> MusicXML
    #
    # 這裡假設前面已產生：
    #
    # melody.musicxml
    #

    musicxml_file = os.path.join(
        job_dir,
        "melody.musicxml"
    )



    clean_xml = os.path.join(
        job_dir,
        "clean.musicxml"
    )



    print("開始 clean_musicxml")



    subprocess.run(
        [
            "python",
            "clean_musicxml.py",
            musicxml_file,
            clean_xml
        ],
        capture_output=False,
        text=True
    )



    print()
    print("清理完成")
    print()



    print("CHECK jianpu input:")
    print(clean_xml)



    ###################################
    # DEBUG MUSICXML
    ###################################


    print("================")
    print("DEBUG MUSICXML")
    print("================")


    try:

        score = converter.parse(
            clean_xml
        )


        for part in score.parts:


            for measure in part.getElementsByClass("Measure"):


                print(
                    "MEASURE",
                    measure.number
                )


                total = 0


                for n in measure.notesAndRests:


                    dur = n.duration.quarterLength


                    print(
                        "offset=",
                        n.offset,
                        "duration=",
                        dur,
                        "end=",
                        n.offset + dur,
                        n
                    )


                    total += dur



                print(
                    "TOTAL=",
                    total
                )


    except Exception as e:

        print(
            "DEBUG ERROR:",
            e
        )



    ###################################
    # jianpu_ly
    ###################################


    print("開始 jianpu_ly")



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
        capture_output=True,
        text=True
    )


    print("================")
    print(result.stdout)
    print(result.stderr)
    print("================")



    return {

        "status":"done",

        "job_id":job_id,

        "clean_musicxml":clean_xml

    }