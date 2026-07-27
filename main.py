import os
import uuid
import subprocess
import shutil

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse


app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
    <body>
    <h2>JianpuTool 簡譜產生器</h2>
    <p>MP3 → MIDI → MusicXML → 簡譜 PDF</p>

    <form action="/upload" method="post" enctype="multipart/form-data">
        <input type="file" name="file">
        <button type="submit">開始轉換</button>
    </form>

    </body>
    </html>
    """


def run_cmd(cmd):
    print("RUN:", " ".join(cmd))

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    print(result.stdout)

    return result.returncode, result.stdout



@app.post("/upload")
async def upload(file: UploadFile = File(...)):

    job = str(uuid.uuid4())

    work = os.path.join(
        "outputs",
        job
    )

    os.makedirs(work, exist_ok=True)


    # =========================
    # 保存 MP3
    # =========================

    mp3 = os.path.join(
        work,
        file.filename
    )

    with open(mp3, "wb") as f:
        shutil.copyfileobj(
            file.file,
            f
        )

    print("MP3保存完成")
    print(mp3)



    # =========================
    # BasicPitch
    # =========================

    midi = os.path.join(
        work,
        "melody.mid"
    )


    code, out = run_cmd(
        [
            "python",
            "basicpitch_convert.py",
            mp3,
            midi
        ]
    )


    if code != 0:
        return {
            "error":"BasicPitch失敗",
            "log":out
        }


    print("MIDI完成")



    # =========================
    # MIDI → MusicXML
    # =========================

    musicxml = os.path.join(
        work,
        "input.musicxml"
    )


    code, out = run_cmd(
        [
            "python",
            "midi_to_musicxml.py",
            midi,
            musicxml
        ]
    )


    if code != 0:
        return {
            "error":"MusicXML失敗",
            "log":out
        }


    print("MusicXML完成")



    # =========================
    # Clean MusicXML
    # =========================

    clean = os.path.join(
        work,
        "clean.musicxml"
    )


    code, out = run_cmd(
        [
            "python",
            "clean_musicxml.py",
            musicxml,
            clean
        ]
    )


    if code != 0:
        return {
            "error":"clean失敗",
            "log":out
        }


    print("清理完成")



    # =========================
    # 新增：MusicXML量化
    # =========================

    fixed = os.path.join(
        work,
        "fixed.musicxml"
    )


    code, out = run_cmd(
        [
            "python",
            "quantize_musicxml.py",
            clean,
            fixed
        ]
    )


    if code != 0:
        return {
            "error":"quantize失敗",
            "log":out
        }


    print("量化完成")



    # =========================
    # jianpu_ly
    # =========================

    ly = os.path.join(
        work,
        "jianpu.ly"
    )


    code, out = run_cmd(
        [
            "python",
            "-m",
            "jianpu_ly",
            fixed,
            "-o",
            ly
        ]
    )


    print(
        "jianpu_ly return:",
        code
    )


    if code != 0:
        return {
            "error":"jianpu_ly失敗",
            "log":out
        }


    print("jianpu.ly完成")



    # =========================
    # LilyPond PDF
    # =========================

    code, out = run_cmd(
        [
            "lilypond",
            "-o",
            os.path.join(work,"result"),
            ly
        ]
    )


    if code != 0:
        return {
            "error":"LilyPond失敗",
            "log":out
        }



    pdf = os.path.join(
        work,
        "result.pdf"
    )


    if os.path.exists(pdf):

        return FileResponse(
            pdf,
            media_type="application/pdf",
            filename="jianpu.pdf"
        )


    return {
        "error":"PDF不存在",
        "folder":work
    }