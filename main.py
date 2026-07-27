import os
import uuid
import subprocess

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse


app = FastAPI()



@app.get("/", response_class=HTMLResponse)
def home():

    return """
    <!DOCTYPE html>

    <html>

    <head>

        <meta charset="utf-8">

        <title>JianpuTool</title>


        <style>

        body {

            font-family: Arial;
            text-align: center;
            margin-top: 80px;

        }


        h1 {

            font-size: 40px;

        }


        h2 {

            color: #555;

        }


        input {

            font-size:18px;

        }


        button {

            font-size:20px;
            padding:10px 40px;

        }


        </style>


    </head>



    <body>


    <h1>
    JianpuTool 簡譜產生器
    </h1>


    <h2>
    MP3 → MIDI → MusicXML → 簡譜 PDF
    </h2>



    <form action="/upload"
          method="post"
          enctype="multipart/form-data">


        <input type="file"
               name="file"
               accept=".mp3,.wav">


        <br><br>


        <button type="submit">
        開始轉換
        </button>


    </form>



    </body>


    </html>
    """




def run_cmd(cmd):

    print("RUN:")
    print(" ".join(cmd))


    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )


    print(result.stdout)

    return result





@app.post("/upload")
async def upload(file: UploadFile = File(...)):


    work_dir = os.path.join(
        "outputs",
        str(uuid.uuid4())
    )


    os.makedirs(
        work_dir,
        exist_ok=True
    )



    input_audio = os.path.join(
        work_dir,
        file.filename
    )



    with open(input_audio,"wb") as f:

        f.write(await file.read())



    print("================")
    print("收到:")
    print(file.filename)
    print("================")
    print("MP3保存完成")




    # BasicPitch

    midi_file=os.path.join(
        work_dir,
        "melody.mid"
    )


    print("開始 BasicPitch")



    result=run_cmd(
        [
            "python",
            "basic_pitch_convert.py",
            input_audio,
            midi_file
        ]
    )



    if result.returncode !=0:

        return {
            "error":"BasicPitch failed",
            "log":result.stdout
        }






    # Quantize


    clean_midi=os.path.join(
        work_dir,
        "melody_clean.mid"
    )


    print("開始 MIDI Quantize")



    result=run_cmd(
        [
            "python",
            "midi_quantize.py",
            midi_file,
            clean_midi
        ]
    )



    if result.returncode !=0:

        return {
            "error":"quantize failed",
            "log":result.stdout
        }







    # MIDI -> MusicXML


    musicxml=os.path.join(
        work_dir,
        "input.musicxml"
    )


    print("MIDI轉MusicXML")



    result=run_cmd(
        [
            "python",
            "midi_to_musicxml.py",
            clean_midi,
            musicxml
        ]
    )



    if result.returncode !=0:

        return {
            "error":"musicxml failed",
            "log":result.stdout
        }







    # Clean MusicXML


    clean_xml=os.path.join(
        work_dir,
        "clean.musicxml"
    )


    print("清理 MusicXML")



    result=run_cmd(
        [
            "python",
            "clean_musicxml.py",
            musicxml,
            clean_xml
        ]
    )



    if result.returncode !=0:

        return {
            "error":"clean_musicxml failed",
            "log":result.stdout
        }



    if not os.path.exists(clean_xml):

        return {
            "error":"clean.musicxml not created"
        }







    # Jianpu


    ly_file=os.path.join(
        work_dir,
        "jianpu.ly"
    )


    print("產生簡譜")



    result=run_cmd(
        [
            "python",
            "-m",
            "jianpu_ly",
            clean_xml
        ]
    )



    if result.returncode !=0:

        return {
            "error":"jianpu_ly failed",
            "log":result.stdout
        }



    with open(
        ly_file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(result.stdout)






    if os.path.getsize(ly_file)==0:

        return {
            "error":"empty ly file"
        }







    # LilyPond


    print("產生PDF")



    result=run_cmd(
        [
            "lilypond",
            "-o",
            work_dir,
            ly_file
        ]
    )



    pdf_file=os.path.join(
        work_dir,
        "jianpu.pdf"
    )



    if not os.path.exists(pdf_file):

        return {

            "error":"PDF failed",

            "log":result.stdout

        }






    return FileResponse(

        pdf_file,

        media_type="application/pdf",

        filename="jianpu.pdf"

    )