import os
import uuid
import subprocess

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse


app = FastAPI()


BASE_DIR = "/app"
OUTPUT_DIR = "/app/outputs"


os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


@app.get("/")
def home():
    return {
        "message": "JianpuTool MIDI → Jianpu PDF"
    }



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


    print("====================")
    print("開始任務:", job_id)
    print("====================")


    # -----------------------
    # save mp3
    # -----------------------

    mp3_path = os.path.join(
        job_dir,
        file.filename
    )


    with open(mp3_path, "wb") as f:
        f.write(
            await file.read()
        )


    print("MP3保存完成")
    print(mp3_path)



    # -----------------------
    # MP3 -> MIDI
    # -----------------------

    midi_path = os.path.join(
        job_dir,
        "melody.mid"
    )


    cmd = [
        "python",
        "basicpitch_convert.py",
        mp3_path,
        midi_path
    ]


    print(
        "RUN:",
        " ".join(cmd)
    )


    subprocess.run(
        cmd,
        check=True
    )


    print("MIDI完成")



    # -----------------------
    # MIDI -> MusicXML
    # -----------------------

    xml_path = os.path.join(
        job_dir,
        "input.musicxml"
    )


    cmd = [
        "python",
        "midi_to_musicxml.py",
        midi_path,
        xml_path
    ]


    print(
        "RUN:",
        " ".join(cmd)
    )


    subprocess.run(
        cmd,
        check=True
    )


    print("MusicXML完成")



    # -----------------------
    # CLEAN MUSICXML
    # -----------------------

    clean_xml = os.path.join(
        job_dir,
        "clean.musicxml"
    )


    cmd = [
        "python",
        "clean_musicxml.py",
        xml_path,
        clean_xml
    ]


    print(
        "RUN:",
        " ".join(cmd)
    )


    subprocess.run(
        cmd,
        check=True
    )


    print("清理完成")



    # =================================================
    # NEW: JIANPU PREPARE V2
    # =================================================


    prepared_xml = os.path.join(
        job_dir,
        "prepared.musicxml"
    )


    print("====================")
    print("開始 jianpu_prepare_v2")
    print("====================")


    cmd = [
        "python",
        "jianpu_prepare_v2.py",
        clean_xml,
        prepared_xml
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


    if result.stderr:
        print(result.stderr)



    if result.returncode != 0:
        raise Exception(
            "jianpu_prepare_v2 failed"
        )


    print("V2完成")
    print(prepared_xml)



    # -----------------------
    # MusicXML -> Jianpu LY
    # -----------------------

    ly_path = os.path.join(
        job_dir,
        "output.ly"
    )


    print("====================")
    print("開始 jianpu_ly")
    print("====================")


    cmd = [
        "python",
        "-m",
        "jianpu_ly",
        prepared_xml
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


    if result.stderr:
        print(result.stderr)



    if result.returncode != 0:
        raise Exception(
            "jianpu_ly failed"
        )


    print("jianpu_ly完成")



    # -----------------------
    # 找 ly
    # -----------------------

    for f in os.listdir(job_dir):

        if f.endswith(".ly"):

            ly_path = os.path.join(
                job_dir,
                f
            )



    # -----------------------
    # LilyPond PDF
    # -----------------------

    pdf_path = ly_path.replace(
        ".ly",
        ".pdf"
    )


    cmd = [
        "lilypond",
        "-o",
        ly_path.replace(".ly",""),
        ly_path
    ]


    print(
        "RUN:",
        " ".join(cmd)
    )


    subprocess.run(
        cmd,
        check=True
    )


    print("PDF完成")



    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )