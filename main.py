from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from melody_cleaner import extract_melody

import shutil
import uuid


from converter import convert_musicxml


print("MAIN VERSION MIDI MELODY MVP")


app = FastAPI()



# =========================
# HTML
# =========================

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)



@app.get("/", response_class=HTMLResponse)
def home():

    with open(
        "static/index.html",
        "r",
        encoding="utf-8"
    ) as f:

        return f.read()



@app.get("/test")
def test():

    return {
        "message": "JianpuTool MVP OK"
    }



# =========================
# MusicXML → Jianpu PDF
# =========================

@app.post("/convert")
async def convert(
    file: UploadFile = File(...)
):

    uid = str(uuid.uuid4())


    xml_file = (
        f"/tmp/{uid}.musicxml"
    )


    with open(
        xml_file,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )


    print(
        "MusicXML:",
        xml_file
    )



    try:

        pdf = convert_musicxml(
             clean_xml
        )


    except Exception as e:

        print(
            "CONVERTER ERROR:",
            e
        )

        return {
            "error": str(e)
        }



    return FileResponse(
        pdf,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )




# =========================
# MIDI → MusicXML → Jianpu
# =========================

@app.post("/midi")
async def midi_convert(
    file: UploadFile = File(...)
):


    uid = str(uuid.uuid4())


    midi_file = (
        f"/tmp/{uid}.mid"
    )

    xml_file = (
        f"/tmp/{uid}.musicxml"
    )



    # 儲存 MIDI

    with open(
        midi_file,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )


    print(
        "MIDI:",
        midi_file
    )



    # =====================
    # MIDI → MusicXML
    # =====================

    from music21 import converter


    score = converter.parse(
        midi_file
    )


    print(
        "MIDI Parts:",
        len(score.parts)
    )



    # MVP:
    # 先只保留第一軌

    if len(score.parts) > 0:

        score = score.parts[0]



    score.write(
        "musicxml",
        fp=xml_file
    )


    print(
        "MusicXML:",
        xml_file
    )



    # =====================
    # MusicXML → PDF
    # =====================


    try:

        pdf = convert_musicxml(
            xml_file
        )


    except Exception as e:

        print(
            "CONVERTER ERROR:",
            e
        )

        return {
            "error": str(e)
        }



    print(
        "PDF:",
        pdf
    )


    return FileResponse(
        pdf,
        media_type="application/pdf",
        filename="jianpu.pdf"
    )