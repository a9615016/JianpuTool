
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse
from pathlib import Path
import tempfile

from music21 import converter as music_converter
from converter import convert_musicxml


app = FastAPI()


@app.get("/")
def home():

    return HTMLResponse("""
    <html>
    <body>

    <h1>JianpuTool</h1>

    <h2>MIDI → 簡譜 PDF</h2>

    <form action="/midi" method="post" enctype="multipart/form-data">

        <input type="file" name="file">
        <button type="submit">
            Convert MIDI
        </button>

    </form>


    <h2>MusicXML → 簡譜 PDF</h2>

    <form action="/musicxml" method="post" enctype="multipart/form-data">

        <input type="file" name="file">
        <button type="submit">
            Convert MusicXML
        </button>

    </form>


    </body>
    </html>
    """)



@app.post("/midi")
async def midi(file: UploadFile = File(...)):

    try:

        temp = tempfile.gettempdir()

        midi_path = Path(temp) / file.filename


        with open(midi_path, "wb") as f:
            f.write(await file.read())


        print("MIDI:", midi_path)



        # MIDI → MusicXML

        score = music_converter.parse(
            str(midi_path)
        )


        musicxml_path = (
            Path(temp)
            /
            (midi_path.stem + ".musicxml")
        )


        score.write(
            "musicxml",
            fp=str(musicxml_path)
        )


        print("MusicXML:", musicxml_path)



        # MusicXML → PDF

        pdf = convert_musicxml(
            str(musicxml_path)
        )


        print("PDF:", pdf)


        return FileResponse(
            pdf,
            media_type="application/pdf",
            filename="jianpu.pdf"
        )


    except Exception as e:

        print("====== MIDI ERROR ======")
        print(e)
        print("========================")

        return {
            "error": str(e)
        }



@app.post("/musicxml")
async def musicxml(file: UploadFile = File(...)):

    try:

        temp = tempfile.gettempdir()

        xml_path = Path(temp) / file.filename


        with open(xml_path, "wb") as f:
            f.write(await file.read())


        print("MusicXML:", xml_path)



        pdf = convert_musicxml(
            str(xml_path)
        )


        return FileResponse(
            pdf,
            media_type="application/pdf",
            filename="jianpu.pdf"
        )


    except Exception as e:

        print("====== MUSICXML ERROR ======")
        print(e)
        print("============================")

        return {
            "error": str(e)
        }

