import os
import uuid
import subprocess
import shutil

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse


app = FastAPI()


BASE_DIR = os.getcwd()


@app.get("/")
def home():
    return HTMLResponse("""
    <html>
    <body>
    <h2>JianpuTool 簡譜產生器</h2>

    <form action="/upload" method="post" enctype="multipart/form-data">
        <input type="file" name="file">
        <button type="submit">開始轉換</button>
    </form>

    </body>
    </html>
    """)


def run_cmd(cmd):

    print("RUN:", " ".join(cmd))

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

    task_id = str(uuid.uuid4())

    work_dir = os.path.abspath(
        os.path.join("outputs", task_id)
    )

    os.makedirs(work_dir, exist_ok=True)


    print("====================")
    print("開始任務:", task_id)
    print("收到:", file.filename)


    # ----------------------
    # MP3
    # ----------------------

    mp3 = os.path.join(
        work_dir,
        file.filename
    )


    with open(mp3,"wb") as f:
        shutil.copyfileobj(
            file.file,
            f
        )


    print("MP3保存完成")
    print(mp3)



    # ----------------------
    # BasicPitch
    # ----------------------

    midi = os.path.join(
        work_dir,
        "melody.mid"
    )


    r = run_cmd([
        "python",
        "basicpitch_convert.py",
        mp3,
        midi
    ])


    if not os.path.exists(midi):

        return {
            "error":"BasicPitch失敗",
            "log":r.stdout
        }


    print("MIDI完成")



    # ----------------------
    # MIDI -> MusicXML
    # ----------------------

    xml = os.path.join(
        work_dir,
        "input.musicxml"
    )


    r = run_cmd([
        "python",
        "midi_to_musicxml.py",
        midi,
        xml
    ])


    if not os.path.exists(xml):

        return {
            "error":"MusicXML失敗"
        }


    print("MusicXML完成")



    # ----------------------
    # clean musicxml
    # ----------------------

    clean_xml = os.path.join(
        work_dir,
        "clean.musicxml"
    )


    r = run_cmd([
        "python",
        "clean_musicxml.py",
        xml,
        clean_xml
    ])



    if not os.path.exists(clean_xml):

        return {
            "error":"clean.musicxml不存在",
            "log":r.stdout
        }


    print("清理完成")


    # ★★★ 修正重點 ★★★

    clean_xml_abs = os.path.abspath(clean_xml)


    print("CHECK jianpu input:")
    print(clean_xml_abs)

    if not os.path.exists(clean_xml_abs):

        return {
            "error":"找不到 clean.musicxml",
            "path":clean_xml_abs
        }



    # ----------------------
    # jianpu_ly
    # ----------------------

    print("開始 jianpu_ly")


    r = run_cmd([
        "python",
        "-m",
        "jianpu_ly",
        clean_xml_abs
    ])


    if r.returncode != 0:

        return {
            "error":"jianpu_ly失敗",
            "log":r.stdout
        }



    ly_file = None


    for f in os.listdir(work_dir):

        if f.endswith(".ly"):

            ly_file = os.path.join(
                work_dir,
                f
            )

            break



    if ly_file is None:

        return {
            "error":"沒有產生 ly"
        }



    print("LY完成:")
    print(ly_file)



    # ----------------------
    # LilyPond PDF
    # ----------------------

    print("開始 LilyPond")


    r = run_cmd([
        "lilypond",
        "-o",
        work_dir,
        ly_file
    ])



    pdf = None


    for f in os.listdir(work_dir):

        if f.endswith(".pdf"):

            pdf=os.path.join(
                work_dir,
                f
            )

            break



    if pdf is None:

        return {
            "error":"PDF產生失敗",
            "log":r.stdout
        }



    print("PDF完成")
    print(pdf)



    return FileResponse(
        pdf,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )