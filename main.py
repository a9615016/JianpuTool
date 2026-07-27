import os
import uuid
import shutil
import subprocess
import xml.etree.ElementTree as ET

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse


app = FastAPI()


BASE = "outputs"


os.makedirs(BASE, exist_ok=True)


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



def run_cmd(cmd, cwd=None):

    print("RUN:", " ".join(cmd))

    result = subprocess.run(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    print(result.stdout)

    return result



# 修正 jianpu_ly 不接受的 duration
def fix_musicxml_duration(xml_file):

    print("修正 MusicXML duration")

    tree = ET.parse(xml_file)
    root = tree.getroot()


    mapping = {
        "9.75": "8",
        "9": "8",
        "7": "6",
        "5": "4",
        "3.5": "4"
    }


    for tag in root.iter():

        if tag.tag.endswith("duration"):

            if tag.text in mapping:
                print(
                    "duration:",
                    tag.text,
                    "->",
                    mapping[tag.text]
                )

                tag.text = mapping[tag.text]


    tree.write(
        xml_file,
        encoding="utf-8",
        xml_declaration=True
    )


    return xml_file



@app.post("/upload")
async def upload(file: UploadFile = File(...)):


    task = str(uuid.uuid4())

    work = os.path.join(BASE, task)

    os.makedirs(work)


    print("====================")
    print("開始任務:", task)
    print("收到:", file.filename)



    mp3 = os.path.join(work, file.filename)


    with open(mp3,"wb") as f:
        shutil.copyfileobj(
            file.file,
            f
        )


    print("MP3保存完成")
    print(mp3)



    # ==========================
    # BasicPitch
    # ==========================

    print("開始 BasicPitch")


    midi = os.path.join(
        work,
        "melody.mid"
    )


    result = run_cmd(
        [
            "python",
            "basicpitch_convert.py",
            mp3,
            midi
        ]
    )


    if not os.path.exists(midi):

        return {
            "error":
            "BasicPitch失敗",
            "log":
            result.stdout
        }



    print("MIDI完成")



    # ==========================
    # MIDI -> MusicXML
    # ==========================


    print("開始 MIDI轉MusicXML")


    musicxml = os.path.join(
        work,
        "input.musicxml"
    )


    result = run_cmd(
        [
            "python",
            "midi_to_musicxml.py",
            midi,
            musicxml
        ]
    )


    if not os.path.exists(musicxml):

        return {
            "error":"MusicXML失敗",
            "log":result.stdout
        }



    print("MusicXML完成")



    # ==========================
    # clean
    # ==========================

    print("開始清理 MusicXML")


    clean = os.path.join(
        work,
        "clean.musicxml"
    )


    result = run_cmd(
        [
            "python",
            "clean_musicxml.py",
            musicxml,
            clean
        ]
    )


    if not os.path.exists(clean):

        return {
            "error":"clean失敗",
            "log":result.stdout
        }


    print("清理完成")



    # ==========================
    # 新增修正
    # ==========================

    fix_musicxml_duration(clean)



    # ==========================
    # jianpu_ly
    # ==========================


    print("開始 jianpu_ly")


    ly = os.path.join(
        work,
        "jianpu.ly"
    )


    result = run_cmd(
        [
            "python",
            "-m",
            "jianpu_ly",
            clean
        ],
        cwd=work
    )


    # jianpu_ly 預設輸出檢查

    generated = os.path.join(
        work,
        "clean.ly"
    )


    if os.path.exists(generated):

        shutil.move(
            generated,
            ly
        )


    if not os.path.exists(ly):

        return {
            "error":"jianpu_ly失敗",
            "log":result.stdout
        }



    print("jianpu完成")



    # ==========================
    # LilyPond
    # ==========================


    print("開始 LilyPond")


    result = run_cmd(
        [
            "lilypond",
            "-o",
            "output",
            ly
        ],
        cwd=work
    )


    pdf = os.path.join(
        work,
        "output.pdf"
    )


    if not os.path.exists(pdf):

        return {
            "error":"PDF產生失敗",
            "log":result.stdout
        }



    print("完成PDF")



    return FileResponse(
        pdf,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )