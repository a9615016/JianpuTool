import os
import uuid
import shutil
import subprocess

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse

import music21


app = FastAPI()


OUTPUT_DIR = "outputs"

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)



# ==========================
# MusicXML Cleaner
# ==========================

def clean_musicxml(input_file):

    print("開始 MusicXML 強力清理")


    score = music21.converter.parse(
        input_file
    )


    for part in score.parts:


        # 移除多聲部

        for measure in part.getElementsByClass(
            "Measure"
        ):

            voices = measure.getElementsByClass(
                "Voice"
            )

            if len(voices):

                for v in list(voices):

                    measure.remove(v)



        # chord 只留第一個音

        for c in list(
            part.recurse()
            .getElementsByClass(
                "Chord"
            )
        ):

            if len(c.notes):

                n = c.notes[0]

                c.activeSite.replace(
                    c,
                    n
                )



        # 移除裝飾音

        for n in list(
            part.recurse()
            .notes
        ):

            try:

                if n.duration.isGrace:

                    n.activeSite.remove(
                        n
                    )

            except:

                pass



        # 修正錯誤 duration

        for n in part.recurse().notesAndRests:

            try:

                if n.duration.quarterLength <= 0:

                    n.duration.quarterLength = 0.25


                if n.duration.quarterLength < 0.0625:

                    n.duration.quarterLength = 0.25


            except:

                pass



    # 重新量化

    try:

        score.quantize(
            quarterLengthDivisors=[
                4,
                8,
                16
            ]
        )

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





# ==========================
# jianpu_ly + LilyPond
# ==========================

def generate_pdf(xml_file):


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



    result = subprocess.run(

        [
            "python",
            "-m",
            "jianpu_ly",
            xml_file
        ],

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


    result2=subprocess.run(

        [
            "lilypond",
            "-o",
            ly_file.replace(
                ".ly",
                ""
            ),
            ly_file
        ],

        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True

    )



    if result2.returncode != 0:

        raise Exception(
            result2.stderr
        )


    return pdf_file







# ==========================
# 首頁
# ==========================

@app.get("/")
def index():

    return {

        "status":
        "JianpuTool running",

        "api":
        [
            "/convert",
            "/midi"
        ]

    }







# ==========================
# MusicXML → PDF
# ==========================

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







# ==========================
# MIDI → PDF
# ==========================

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


    score=music21.converter.parse(
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