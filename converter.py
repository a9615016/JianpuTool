import os
import tempfile
import subprocess
import uuid

from music21 import converter as music_converter


def run_lilypond(ly_file):

    output_dir = os.path.dirname(ly_file)

    result = subprocess.run(
        [
            "lilypond",
            "-o",
            os.path.join(
                output_dir,
                "jianpu_output"
            ),
            ly_file
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        raise Exception(
            "LilyPond Error:\n" +
            result.stderr
        )

    pdf_file = os.path.join(
        output_dir,
        "jianpu_output.pdf"
    )

    return pdf_file



def musicxml_to_pdf(musicxml_file):

    temp_dir = tempfile.gettempdir()

    name = str(uuid.uuid4())

    ly_file = os.path.join(
        temp_dir,
        name + ".ly"
    )


    # MusicXML → Jianpu Lilypond

    with open(
        ly_file,
        "w",
        encoding="utf-8"
    ) as f:

        process = subprocess.run(
            [
                "python",
                "-m",
                "jianpu_ly",
                musicxml_file
            ],
            stdout=f,
            stderr=subprocess.PIPE,
            text=True
        )


    if process.returncode != 0:

        raise Exception(
            "jianpu-ly error:\n"
            + process.stderr
        )


    return run_lilypond(
        ly_file
    )




def midi_to_pdf(midi_file):

    temp_dir = tempfile.gettempdir()

    name = str(uuid.uuid4())


    musicxml_file = os.path.join(
        temp_dir,
        name + ".musicxml"
    )


    # MIDI → MusicXML

    score = music_converter.parse(
        midi_file
    )

    score.write(
        "musicxml",
        fp=musicxml_file
    )


    # MusicXML → PDF

    return musicxml_to_pdf(
        musicxml_file
    )




def convert_musicxml(
        input_file
):

    return musicxml_to_pdf(
        input_file
    )