# main.py
# JianpuTool v26 DEBUG VERSION
# MP3/WAV -> MusicXML -> clean -> jianpu_ly


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
        <!DOCTYPE html>
        <html>

        <head>
        <title>JianpuTool</title>
        </head>

        <body>

        <h1>
        JianpuTool 簡譜產生器
        </h1>

        <p>
        MP3/WAV → MusicXML → 簡譜 PDF
        </p>


        <form action="/upload"
              method="post"
              enctype="multipart/form-data">


        <input type="file"
               name="file"
               accept=".mp3,.wav">


        <button type="submit">
        Upload
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



    ################################################
    # 1. 這裡接你的 MP3 -> MIDI -> MusicXML
    ################################################


    # 假設最後產生:
    #
    # melody.musicxml
    #


    musicxml_file = os.path.join(
        job_dir,
        "melody.musicxml"
    )



    ################################################
    # 如果你已有 MusicXML
    # 直接測試下面流程
    ################################################



    clean_xml = os.path.join(
        job_dir,
        "clean.musicxml"
    )



    print("開始 clean_musicxml")


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


    clean_result = subprocess.run(

        cmd_clean,

        capture_output=True,

        text=True

    )


    print(clean_result.stdout)

    print(clean_result.stderr)




    ################################################
    # DEBUG MUSICXML
    ################################################


    print("================")
    print("CHECK jianpu input:")
    print(clean_xml)
    print("================")



    print("================")
    print("DEBUG NOTES")
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
                    "MEASURE TOTAL:",
                    measure.duration.quarterLength
                )



    except Exception as e:


        print(
            "DEBUG ERROR:",
            e
        )




    ################################################
    # 2. jianpu_ly
    ################################################



    print("開始 jianpu_ly")



    cmd_jianpu = [

        "python",

        "-m",

        "jianpu_ly",

        clean_xml

    ]



    print(

        "RUN:",

        " ".join(cmd_jianpu)

    )



    result = subprocess.run(

        cmd_jianpu,

        capture_output=True,

        text=True

    )



    print("================")
    print("jianpu stdout")
    print("================")

    print(
        result.stdout
    )



    print("================")
    print("jianpu stderr")
    print("================")


    print(
        result.stderr
    )




    ################################################
    # 回傳
    ################################################



    return {


        "status":"done",


        "job_id":job_id,


        "folder":job_dir,


        "clean_musicxml":clean_xml

    }