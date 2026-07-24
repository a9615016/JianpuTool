import os
import uuid
import subprocess
import shutil

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse

import music21


app = FastAPI(
    title="JianpuTool"
)


OUTPUT_DIR = "outputs"

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)



# =========================
# MusicXML 清理
# =========================

def clean_musicxml(input_file):

    print("開始 MusicXML 清理")


    score = music21.converter.parse(
        input_file
    )


    for part in score.parts:


        # 移除 Voice

        for measure in part.getElementsByClass(
            "Measure"
        ):

            voices = measure.getElementsByClass(
                "Voice"
            )

            for v in voices:

                measure.remove(v)



        # chord只留最高音

        chords = list(
            part.recurse()
            .getElementsByClass(
                "Chord"
            )
        )


        for c in chords:

            if len(c.notes) > 0:

                n = c.notes[-1]

                c.activeSite.replace(
                    c,
                    n
                )



        # 修正過短音符

        for n in part.recurse().notesAndRests:


            try:

                if n.duration.quarterLength < 0.0625:

                    n.duration.quarterLength = 0.25


            except:

                pass



    output = input_file.replace(
        ".musicxml",
        "_clean.musicxml"
    )


    score.write(
        "musicxml",
        fp=output
    )


    print(
        "清理完成:",
        output
    )


    return output





# =========================
# jianpu_ly + lilypond
# =========================

def generate_pdf(xml_file):


    folder = os.path.dirname(
        xml_file
    )


    ly_file = xml_file.replace(
        ".musicxml",
        ".ly"
    )


    pdf_file = xml_file.replace(
        ".musicxml",
        ".pdf"
    )



    print(
        "開始 jianpu_ly"
    )



    cmd = [
        "python",
        "-m",
        "jianpu_ly",
        xml_file
    ]


    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )



    print(
        "jianpu_ly return:",
        result.returncode
    )



    if result.returncode != 0:

        raise Exception(
            result.stderr
        )



    with open(
        ly_file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            result.stdout
        )



    print(
        "開始 LilyPond"
    )


    lily = [
        "lilypond",
        "-o",
        ly_file.replace(
            ".ly",
            ""
        ),
        ly_file
    ]



    result2 = subprocess.run(
        lily,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )



    if result2.returncode != 0:

        raise Exception(
            result2.stderr
        )



    return pdf_file





# =========================
# 首頁
# =========================

@app.get("/")
def home():

    return {
        "status":
        "JianpuTool running",

        "api":
        [
            "/convert",
            "/midi"
        ]
    }





# =========================
# MusicXML → PDF
# =========================

@app.post("/convert")
async def convert(
    file:UploadFile=File(...)
):


    uid=str(uuid.uuid4())


    folder=os.path.join(
        OUTPUT_DIR,
        uid
    )


    os.makedirs(
        folder,
        exist_ok=True
    )


    xml=os.path.join(
        folder,
        file.filename
    )


    with open(
        xml,
        "wb"
    ) as f:

        shutil.copyfileobj(
            file.file,
            f
        )



    clean=clean_musicxml(
        xml
    )


    pdf=generate_pdf(
        clean
    )


    return FileResponse(
        pdf,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )







# =========================
# MIDI → MusicXML → PDF
# =========================

@app.post("/midi")
async def midi_convert(
    file:UploadFile=File(...)
):


    uid=str(uuid.uuid4())


    folder=os.path.join(
        OUTPUT_DIR,
        uid
    )


    os.makedirs(
        folder,
        exist_ok=True
    )


    mid=os.path.join(
        folder,
        file.filename
    )



    with open(
        mid,
        "wb"
    ) as f:

        shutil.copyfileobj(
            file.file,
            f
        )



    print(
        "開始 MIDI → MusicXML"
    )



    score = music21.converter.parse(
        mid
    )



    xml=mid.replace(
        ".mid",
        ".musicxml"
    )



    score.write(
        "musicxml",
        fp=xml
    )



    print(
        xml
    )



    clean=clean_musicxml(
        xml
    )



    pdf=generate_pdf(
        clean
    )



    return FileResponse(
        pdf,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )