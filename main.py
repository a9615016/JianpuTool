import os
import uuid
import subprocess
import shutil

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse


app = FastAPI()


BASE_DIR = "outputs"

os.makedirs(BASE_DIR, exist_ok=True)



@app.get("/")
def home():

    return HTMLResponse(
"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>JianpuTool</title>
</head>

<body>

<h1>JianpuTool</h1>

<form action="/convert" method="post" enctype="multipart/form-data">

<input type="file" name="file">

<button type="submit">
轉換簡譜 PDF
</button>

</form>

</body>
</html>
"""
    )



@app.post("/convert")
async def convert(file: UploadFile = File(...)):

    try:

        job = str(uuid.uuid4())

        folder = os.path.join(
            BASE_DIR,
            job
        )

        os.makedirs(folder, exist_ok=True)


        # 上傳 MusicXML
        input_xml = os.path.join(
            folder,
            "input.musicxml"
        )


        with open(input_xml,"wb") as f:
            shutil.copyfileobj(
                file.file,
                f
            )


        print("開始 MusicXML -> jianpu")
        print("輸入:",input_xml)



        # ==========================
        # 1. clean MusicXML
        # ==========================

        clean_xml = os.path.join(
            folder,
            "clean.musicxml"
        )


        result = subprocess.run(
            [
                "python",
                "clean_musicxml.py",
                input_xml,
                clean_xml
            ],
            capture_output=True,
            text=True
        )


        print(result.stdout)
        print("clean完成")


        if not os.path.exists(clean_xml):

            clean_xml=input_xml



        # ==========================
        # 2. jianpu_ly
        # ==========================

        ly_file=os.path.join(
            folder,
            "output.ly"
        )


        with open(
            ly_file,
            "w",
            encoding="utf-8"
        ) as out:


            result=subprocess.run(
                [
                    "python",
                    "-m",
                    "jianpu_ly",
                    clean_xml
                ],
                stdout=out,
                stderr=subprocess.PIPE,
                text=True
            )


        print(
            "jianpu_ly:",
            result.returncode
        )


        if result.returncode !=0:

            return {
                "error":
                result.stderr
            }



        # ==========================
        # 3. LilyPond PDF
        # ==========================

        pdf_file=os.path.join(
            folder,
            "output.pdf"
        )


        result=subprocess.run(
            [
                "lilypond",
                "-o",
                os.path.join(folder,"output"),
                ly_file
            ],
            capture_output=True,
            text=True
        )


        if not os.path.exists(pdf_file):

            return {
                "error":
                result.stderr
            }


        return FileResponse(
            pdf_file,
            media_type="application/pdf",
            filename="jianpu.pdf"
        )


    except Exception as e:

        return {
            "error":str(e)
        }



@app.post("/midi")
async def midi(file: UploadFile = File(...)):

    return {
        "message":
        "MIDI endpoint OK"
    }