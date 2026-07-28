from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse
import os
import uuid
import subprocess

app = FastAPI()

OUTPUT_DIR = "/app/outputs"

os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.get("/")
def home():
    return HTMLResponse("""
    <h2>JianpuTool 簡譜產生器</h2>
    <form action="/upload" method="post" enctype="multipart/form-data">
        <input type="file" name="file">
        <button type="submit">Upload</button>
    </form>
    """)


@app.post("/upload")
async def upload(file: UploadFile = File(...)):

    job_id = str(uuid.uuid4())
    job_dir = os.path.join(OUTPUT_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)

    input_musicxml = os.path.join(job_dir, "input.musicxml")
    clean_musicxml = os.path.join(job_dir, "clean.musicxml")
    output_ly = os.path.join(job_dir, "output.ly")

    # save upload
    with open(input_musicxml, "wb") as f:
        f.write(await file.read())


    print("================")
    print("MusicXML完成")
    print("================")


    # =========================
    # CLEAN MUSICXML V40
    # =========================

    cmd_clean = [
        "python",
        "clean_musicxmlv40.py",
        input_musicxml,
        clean_musicxml
    ]

    print("RUN:", " ".join(cmd_clean))

    clean = subprocess.run(
        cmd_clean,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    print(clean.stdout)


    if not os.path.exists(clean_musicxml):
        return {
            "error": "clean musicxml failed",
            "log": clean.stdout
        }


    print("清理完成")
    print("CHECK jianpu input:")
    print(clean_musicxml)


    # =========================
    # jianpu_ly
    # =========================

    cmd_jianpu = [
        "python",
        "-m",
        "jianpu_ly",
        clean_musicxml
    ]

    print("開始 jianpu_ly")
    print("RUN:", " ".join(cmd_jianpu))


    ly = subprocess.run(
        cmd_jianpu,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )


    print(ly.stdout)


    if ly.returncode != 0:
        return {
            "error": "jianpu_ly failed",
            "log": ly.stdout
        }


    return {
        "status": "success",
        "folder": job_dir
    }