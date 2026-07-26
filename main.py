import os
import uuid
import subprocess

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse


app = FastAPI()


@app.get("/")
def home():
    return {
        "status": "JianpuTool running",
        "version": "V21.4"
    }



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


    # =====================
    # Save MP3
    # =====================

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



    # =====================
    # BasicPitch
    # =====================

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



    # =====================
    # Quantize
    # =====================


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




    # =====================
    # MIDI -> MusicXML
    # =====================


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



    # =====================
    # Clean MusicXML
    # =====================


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


    print(
        "clean_xml exists:",
        os.path.exists(clean_xml)
    )


    if result.returncode !=0:
        return {
            "error":"clean_musicxml failed",
            "log":result.stdout
        }


    if not os.path.exists(clean_xml):

        return {
            "error":"clean.musicxml not created",
            "log":result.stdout
        }



    # =====================
    # Jianpu
    # =====================


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


    print("jianpu return:",
          result.returncode)


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



    print(
        "LY SIZE:",
        os.path.getsize(ly_file)
    )



    if os.path.getsize(ly_file)==0:

        return {
            "error":"empty ly file"
        }



    # =====================
    # LilyPond PDF
    # =====================


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


    print(
        "PDF exists:",
        os.path.exists(pdf_file)
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