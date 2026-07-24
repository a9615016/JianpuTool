from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse
import subprocess
import uuid
import os
import glob
import music21


app = FastAPI()


LILYPOND = "lilypond"


# ==========================
# 首頁
# ==========================

@app.get("/", response_class=HTMLResponse)
def home():

    return """
    <html>
    <head>
    <meta charset="utf-8">
    <title>JianpuTool</title>
    </head>

    <body>

    <h1>🎵 JianpuTool</h1>

    <h3>MusicXML → 簡譜 PDF</h3>

    <form action="/convert"
    method="post"
    enctype="multipart/form-data">

    <input type="file" name="file">

    <button>
    產生 PDF
    </button>

    </form>


    <hr>


    <h3>MIDI → 簡譜 PDF</h3>


    <form action="/midi"
    method="post"
    enctype="multipart/form-data">

    <input type="file" name="file">

    <button>
    MIDI轉簡譜
    </button>

    </form>


    </body>
    </html>
    """



@app.get("/status")
def status():

    return {
        "status":"JianpuTool MVP OK"
    }





# ==========================
# MusicXML → PDF
# ==========================

def musicxml_to_pdf(
        musicxml_file,
        work_dir
):

    clean_file=os.path.join(
        work_dir,
        "clean.musicxml"
    )


    subprocess.run(
        [
            "python",
            "clean_musicxml.py",
            musicxml_file,
            clean_file
        ],
        check=True
    )


    ly_file=os.path.join(
        work_dir,
        "input.ly"
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
                clean_file
            ],

            stdout=out,

            stderr=subprocess.PIPE,

            text=True
        )



    if result.returncode != 0:

        return None,result.stderr




    result=subprocess.run(

        [
            LILYPOND,
            "input.ly"
        ],

        cwd=work_dir,

        stdout=subprocess.PIPE,

        stderr=subprocess.STDOUT,

        text=True

    )



    if result.returncode != 0:

        return None,result.stdout



    pdfs=glob.glob(

        os.path.join(
            work_dir,
            "*.pdf"
        )

    )


    if not pdfs:

        return None,"PDF not found"



    return pdfs[0],None






# ==========================
# MusicXML 上傳
# ==========================

@app.post("/convert")
async def convert(
        file:UploadFile=File(...)
):

    job=str(uuid.uuid4())


    work_dir=os.path.join(
        "outputs",
        job
    )


    os.makedirs(
        work_dir,
        exist_ok=True
    )



    musicxml_file=os.path.join(
        work_dir,
        "input.musicxml"
    )



    with open(
        musicxml_file,
        "wb"
    ) as f:

        f.write(
            await file.read()
        )



    pdf,error=musicxml_to_pdf(
        musicxml_file,
        work_dir
    )



    if error:

        return {
            "error":error
        }



    return FileResponse(
        pdf,
        filename="jianpu.pdf",
        media_type="application/pdf"
    )







# ==========================
# MIDI 上傳
# ==========================

@app.post("/midi")
async def midi_convert(
        file:UploadFile=File(...)
):

    job=str(uuid.uuid4())


    work_dir=os.path.join(
        "outputs",
        job
    )


    os.makedirs(
        work_dir,
        exist_ok=True
    )



    midi_file=os.path.join(
        work_dir,
        "input.mid"
    )


    musicxml_file=os.path.join(
        work_dir,
        "input.musicxml"
    )



    with open(
        midi_file,
        "wb"
    ) as f:

        f.write(
            await file.read()
        )



    try:

        score=music21.converter.parse(
            midi_file
        )


        from music21 import stream



        new_score=stream.Score()

        new_part=stream.Part()



        # 第一軌

        if len(score.parts)>0:

            part=score.parts[0]

        else:

            part=score



        notes=[]



        # 取得音符

        for n in part.flatten().notes:


            if n.isChord:

                notes.append(
                    n.notes[-1]
                )

            else:

                notes.append(n)



        # 排序

        notes.sort(
            key=lambda x:x.offset
        )



        # 刪除同時間音符

        used=set()


        for n in notes:


            t=round(
                n.offset,
                4
            )


            if t not in used:


                new_part.append(n)

                used.add(t)



        print(
            "單旋律音符數:",
            len(new_part.notes),
            flush=True
        )



        new_score.append(
            new_part
        )



        new_score.write(
            "musicxml",
            fp=musicxml_file
        )



    except Exception as e:


        return {

            "error":"MIDI convert failed",

            "detail":str(e)

        }




    pdf,error=musicxml_to_pdf(
        musicxml_file,
        work_dir
    )



    if error:

        return {
            "error":error
        }



    return FileResponse(
        pdf,
        filename="jianpu.pdf",
        media_type="application/pdf"
    )