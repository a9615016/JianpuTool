from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse
import shutil
import os
import uuid

from converter import midi_to_pdf


app = FastAPI()


@app.get("/")
def home():

    return HTMLResponse("""
<!DOCTYPE html>
<html lang="zh-TW">

<head>
<meta charset="UTF-8">
<title>JianpuTool</title>
</head>

<body>

<h1>
🎵 JianpuTool MIDI → 簡譜
</h1>


<form action="/midi"
method="post"
enctype="multipart/form-data">


<input type="file"
name="file"
accept=".mid,.midi">


<br><br>


<button type="submit">
產生簡譜 PDF
</button>


</form>


</body>

</html>
""")


@app.get("/status")
def status():

    return {
        "status": "JianpuTool MVP OK",
        "api": [
            "/midi"
        ]
    }



@app.post("/midi")
async def midi(
    file: UploadFile = File(...)
):

    os.makedirs(
        "uploads",
        exist_ok=True
    )


    filename = (
        str(uuid.uuid4())
        + ".mid"
    )


    midi_path = os.path.join(
        "uploads",
        filename
    )


    with open(
        midi_path,
        "wb"
    ) as f:

        shutil.copyfileobj(
            file.file,
            f
        )


    try:

        pdf_path = midi_to_pdf(
            midi_path
        )


        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename="jianpu.pdf"
        )


    except Exception as e:

        return {
            "error": str(e)
        }