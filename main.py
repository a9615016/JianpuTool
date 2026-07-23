```python
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse
import os
import tempfile
from pathlib import Path

from music21 import converter as music_converter

from converter import convert_musicxml


app = FastAPI()


@app.get("/")
def home():

    return HTMLResponse("""
    <h1>JianpuTool</h1>

    <h2>MIDI → 簡譜 PDF</h2>

    <form action="/midi" method="post" enctype="multipart/form-data">

        <input type="file" name="file">

        <button type="submit">
        Convert
        </button>

    </form>

    """)



@app.post("/midi")
async def midi(file: UploadFile = File(...)):

    try:

        # 暫存 MIDI
        temp_dir = tempfile.gettempdir()

        midi_path = Path(temp_dir) / file.filename


        with open(midi_path, "wb") as f:

            f.write(await file.read())


        print("MIDI:", midi_path)



        # MIDI -> MusicXML

        score = music_converter.parse(
            str(midi_path)
        )


        musicxml_path = (
            Path(temp_dir)
            /
            (midi_path.stem + ".musicxml")
        )


        score.write(
            "musicxml",
            fp=str(musicxml_path)
        )


        print(
            "MusicXML:",
            musicxml_path
        )



        # MusicXML -> Jianpu PDF

        pdf = convert_musicxml(
            str(musicxml_path)
        )


        print(
            "PDF:",
            pdf
        )


        return FileResponse(
            pdf,
            media_type="application/pdf",
            filename="jianpu.pdf"
        )


    except Exception as e:

        print("===================")
        print("MIDI ERROR")
        print(e)
        print("===================")

        return {
            "error": str(e)
        }



@app.post("/musicxml")
async def musicxml(file: UploadFile = File(...)):

    try:

        temp_dir = tempfile.gettempdir()

        xml_path = Path(temp_dir) / file.filename


        with open(xml_path,"wb") as f:

            f.write(await file.read())


        pdf = convert_musicxml(
            str(xml_path)
        )


        return FileResponse(
            pdf,
            media_type="application/pdf",
            filename="jianpu.pdf"
        )


    except Exception as e:

        print("MUSICXML ERROR")
        print(e)

        return {
            "error": str(e)
        }
```
