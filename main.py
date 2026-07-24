import os
import uuid
import subprocess
import shutil
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse

from clean_musicxml import clean_musicxml


app = FastAPI()


@app.get("/")
def home():
    return HTMLResponse("""
    <h2>JianpuTool</h2>
    <form action="/convert" method="post" enctype="multipart/form-data">
        <input type="file" name="file">
        <button type="submit">Convert</button>
    </form>
    """)



@app.post("/convert")
async def convert(file: UploadFile = File(...)):

    work = "outputs/" + str(uuid.uuid4())
    os.makedirs(work, exist_ok=True)


    input_xml = os.path.join(
        work,
        "input.musicxml"
    )


    with open(input_xml,"wb") as f:
        shutil.copyfileobj(file.file,f)


    print("開始 MusicXML -> jianpu")
    print("輸入:",input_xml)


    clean_xml = os.path.join(
        work,
        "clean.musicxml"
    )


    # 清理 MusicXML
    clean_musicxml(
        input_xml,
        clean_xml
    )


    print("clean完成")


    #
    # 產生 ly
    #
    ly_file = os.path.join(
        work,
        "jianpu.ly"
    )


    cmd=[
        "python",
        "-m",
        "jianpu_ly",
        clean_xml
    ]


    print("jianpu_ly: 1")


    try:

        result=subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )


        if result.returncode !=0:
            print(result.stderr)
            return {
                "error":result.stderr
            }


        with open(
            ly_file,
            "w",
            encoding="utf-8"
        ) as f:
            f.write(result.stdout)



    except Exception as e:

        return {
            "error":str(e)
        }



    #
    # Lilypond PDF
    #
    pdf_file=os.path.join(
        work,
        "jianpu.pdf"
    )


    try:

        subprocess.run(
            [
                "lilypond",
                "-o",
                pdf_file.replace(".pdf",""),
                ly_file
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )


    except Exception as e:

        return {
            "error":"lilypond "+str(e)
        }



    if os.path.exists(pdf_file):

        return FileResponse(
            pdf_file,
            media_type="application/pdf",
            filename="jianpu.pdf"
        )


    return {
        "error":"PDF 產生失敗"
    }