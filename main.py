# main.py
# JianpuTool v26 DEBUG
# MP3 -> BasicPitch -> MIDI -> MusicXML -> Clean -> Jianpu


from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse

import os
import uuid
import subprocess


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
        MP3 → MIDI → MusicXML → Jianpu PDF
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


    mp3_file = os.path.join(
        job_dir,
        file.filename
    )


    with open(mp3_file,"wb") as f:
        f.write(
            await file.read()
        )


    print("====================")
    print("開始任務:",job_id)
    print("收到:",file.filename)
    print("MP3保存完成")
    print(mp3_file)



    #################################
    # BasicPitch
    #################################

    midi_file = os.path.join(
        job_dir,
        "melody.mid"
    )


    cmd = [
        "python",
        "basicpitch_convert.py",
        mp3_file,
        midi_file
    ]


    print(
        "RUN:",
        " ".join(cmd)
    )


    subprocess.run(
        cmd,
        capture_output=False
    )


    print("MIDI完成")



    #################################
    # MIDI -> MusicXML
    #################################

    musicxml_file = os.path.join(
        job_dir,
        "input.musicxml"
    )


    cmd = [
        "python",
        "midi_to_musicxml.py",
        midi_file,
        musicxml_file
    ]


    print(
        "RUN:",
        " ".join(cmd)
    )


    subprocess.run(
        cmd,
        capture_output=False
    )


    print("MusicXML完成")



    #################################
    # CLEAN MUSICXML
    #################################

    clean_xml = os.path.join(
        job_dir,
        "clean.musicxml"
    )


    cmd = [
        "python",
        "clean_musicxml.py",
        musicxml_file,
        clean_xml
    ]


    print(
        "RUN:",
        " ".join(cmd)
    )


    subprocess.run(
        cmd,
        capture_output=False
    )


    print()
    print("清理完成")
    print()



    print("CHECK jianpu input:")
    print(clean_xml)



    #################################
    # DEBUG MUSICXML
    #################################

    print("================")
    print("DEBUG MUSICXML")
    print("================")


    try:

        from music21 import converter


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
                        n.offset+n.duration.quarterLength,
                        n
                    )


                print("----------------")


    except Exception as e:

        print(
            "DEBUG ERROR:",
            e
        )



    #################################
    # jianpu_ly
    #################################

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


    print(result.stdout)

    print(result.stderr)



    return {

        "status":"done",

        "job_id":job_id,

        "clean_musicxml":clean_xml

    }