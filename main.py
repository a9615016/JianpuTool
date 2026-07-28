# main.py
# JianpuTool DEBUG VERSION
# Find jianpu_ly barcheck error


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
        MIDI → MusicXML → Jianpu PDF
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


    with open(input_file, "wb") as f:

        f.write(
            await file.read()
        )


    print("================")
    print("收到:")
    print(file.filename)
    print("================")



    #
    # 你的 MIDI → MusicXML 流程
    #
    # 這裡保持原本產生:
    #
    # input.musicxml
    #

    musicxml_file = os.path.join(
        job_dir,
        "input.musicxml"
    )



    #
    # clean
    #

    clean_xml = os.path.join(
        job_dir,
        "clean.musicxml"
    )



    cmd_clean = [

        "python",

        "clean_musicxml.py",

        musicxml_file,

        clean_xml

    ]


    print(
        "RUN:",
        " ".join(cmd_clean)
    )


    subprocess.run(
        cmd_clean,
        capture_output=False,
        text=True
    )



    print()
    print("清理完成")
    print()



    print("CHECK jianpu input:")
    print(clean_xml)



    ####################################
    # DEBUG MUSICXML
    ####################################


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


                for n in measure.notesAndRests:


                    print(

                        "offset=",
                        n.offset,

                        "duration=",
                        n.duration.quarterLength,

                        "end=",
                        n.offset + n.duration.quarterLength,

                        n

                    )


                print(
                    "----------------"
                )


    except Exception as e:

        print(
            "DEBUG ERROR:",
            e
        )



    ####################################
    # jianpu_ly
    ####################################


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