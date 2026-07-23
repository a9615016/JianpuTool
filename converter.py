import os
import subprocess
import uuid


LILYPOND = (
    r"C:\lilypond-2.26.0\bin\lilypond.exe"
)


def midi_to_pdf(mid_file):


    uid = str(uuid.uuid4())

    xml = f"{uid}.musicxml"
    ly = f"{uid}.ly"


    # MIDI → MusicXML
    subprocess.run(
        [
            "python",
            "-m",
            "music21",
            mid_file
        ],
        check=True
    )


    # 這裡接你之前成功的 MIDI analyzer
    #
    # 例如:
    # analyzer.py
    # output.musicxml


    subprocess.run(
        [
            "python",
            "-m",
            "jianpu_ly",
            xml
        ],
        stdout=open(
            ly,
            "w",
            encoding="utf-8"
        ),
        check=True
    )


    subprocess.run(
        [
            LILYPOND,
            ly
        ],
        check=True
    )


    pdf = ly.replace(
        ".ly",
        ".pdf"
    )


    return pdf