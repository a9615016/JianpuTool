from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
import shutil
import os


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

    path = "uploads/" + file.filename


    with open(path, "wb") as f:

        shutil.copyfileobj(
            file.file,
            f
        )


    return {
        "message": "MIDI upload OK",
        "file": file.filename
    }