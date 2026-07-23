import os
import tempfile
import subprocess
import uuid

from music21 import converter as music_converter


def clean_melody(score):
    """
    保留第一聲部主旋律
    移除 Piano 伴奏
    """

    parts = score.parts

    if len(parts) == 0:
        return score

    # 只保留第一個 Part
    melody = parts[0]

    new_score = melody.stream()

    return new_score



def run_lilypond(ly_file):

    output_dir = os.path.dirname(ly_file)

    output_name = os.path.join(
        output_dir,
        "jianpu_output"
    )


    result = subprocess.run(
        [
            "lilypond",
            "-o",
            output_name,
            ly_file
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )


    if result.returncode != 0:
        raise Exception(
            result.stderr
        )


    return output_name + ".pdf"



def musicxml_to_pdf(
        musicxml_file
):

    temp = tempfile.gettempdir()

    uid = str(uuid.uuid4())


    clean_xml = os.path.join(
        temp,
        uid + "_clean.musicxml"
    )


    ly_file = os.path.join(
        temp,
        uid + ".ly"
    )


    # -----------------------
    # MusicXML 清理
    # -----------------------

    score = music_converter.parse(
        musicxml_file
    )


    score = clean_melody(
        score
    )


    score.write(
        "musicxml",
        fp=clean_xml
    )


    # -----------------------
    # MusicXML → Jianpu ly
    # -----------------------

    with open(
        ly_file,
        "w",
        encoding="utf-8"
    ) as f:

        result = subprocess.run(
            [
                "python",
                "-m",
                "jianpu_ly",
                clean_xml
            ],
            stdout=f,
            stderr=subprocess.PIPE,
            text=True
        )


    if result.returncode != 0:

        raise Exception(
            "jianpu-ly error\n"
            + result.stderr
        )


    # -----------------------
    # ly → PDF
    # -----------------------

    pdf = run_lilypond(
        ly_file
    )


    return pdf



def midi_to_pdf(
        midi_file
):

    temp = tempfile.gettempdir()

    uid = str(uuid.uuid4())


    musicxml = os.path.join(
        temp,
        uid + ".musicxml"
    )


    score = music_converter.parse(
        midi_file
    )


    score.write(
        "musicxml",
        fp=musicxml
    )


    return musicxml_to_pdf(
        musicxml
    )



def convert_musicxml(
        input_file
):

    return musicxml_to_pdf(
        input_file
    )