import os
import uuid
import subprocess
import shutil

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse


app = FastAPI()


BASE_DIR = "outputs"


os.makedirs(BASE_DIR, exist_ok=True)



@app.get("/", response_class=HTMLResponse)
def home():

    return """
    <html>
    <body>
    <h2>JianpuTool</h2>

    <form action="/convert" method="post" enctype="multipart/form-data">

    <input type="file" name="file">

    <button type="submit">
    Convert
    </button>

    </form>

    </body>
    </html>
    """



def run_clean(input_file, output_file):

    print("開始 clean MusicXML")

    subprocess.run(
        [
            "python",
            "clean_musicxml.py",
            input_file,
            output_file
        ],
        check=True
    )

    print("clean完成")
    print(output_file)



def run_jianpu(clean_file, ly_file):

    print("jianpu_ly: 1")


    result = subprocess.run(
        [
            "python",
            "-m",
            "jianpu_ly",
            clean_file
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )


    ly_text = result.stdout


    # 修正 jianpu_ly octave bug
    ly_text = ly_text.replace("1,1", "1")


    with open(
        ly_file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(ly_text)



    if result.returncode != 0:

        print("jianpu_ly error:")
        print(result.stderr)

        raise Exception(result.stderr)



    print("jianpu完成")



def run_lilypond(ly_file):

    print("LilyPond start")


    subprocess.run(
        [
            "lilypond",
            "-o",
            ly_file.replace(".ly",""),
            ly_file
        ],
        check=True
    )


    pdf_file = ly_file.replace(".ly",".pdf")


    return pdf_file





@app.post("/convert")
async def convert(
    file: UploadFile = File(...)
):


    job_id = str(uuid.uuid4())

    folder = os.path.join(
        BASE_DIR,
        job_id
    )

    os.makedirs(folder)


    input_file = os.path.join(
        folder,
        "input.musicxml"
    )


    with open(
        input_file,
        "wb"
    ) as f:

        shutil.copyfileobj(
            file.file,
            f
        )



    print("開始 MusicXML -> jianpu")
    print("輸入:",input_file)



    clean_file = os.path.join(
        folder,
        "clean.musicxml"
    )


    ly_file = os.path.join(
        folder,
        "jianpu.ly"
    )



    try:

        run_clean(
            input_file,
            clean_file
        )


        run_jianpu(
            clean_file,
            ly_file
        )


        pdf = run_lilypond(
            ly_file
        )


        return FileResponse(
            pdf,
            media_type="application/pdf",
            filename="jianpu.pdf"
        )


    except Exception as e:


        return {
            "error":str(e)
        }