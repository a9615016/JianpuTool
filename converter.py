import os
import subprocess
import uuid

from extract_melody import extract_melody



def convert_musicxml(xml_file):


    uid = str(uuid.uuid4())


    work = "/tmp"


    melody_xml = os.path.join(
        work,
        uid + "_melody.musicxml"
    )


    # 先抽主旋律
    extract_melody(
        xml_file,
        melody_xml
    )


    print(
        "Melody XML:",
        melody_xml
    )


    ly_file = os.path.join(
        work,
        uid + ".ly"
    )


    pdf_file = os.path.join(
        work,
        "jianpu.pdf"
    )



    # MusicXML → jianpu ly

    cmd = [
        "python",
        "-m",
        "jianpu_ly",
        melody_xml
    ]


    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )


    if result.returncode != 0:

        print(result.stderr)

        raise Exception(
            "jianpu_ly failed"
        )



    with open(
        ly_file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(result.stdout)



    # Lilypond PDF

    lilypond = [
        "lilypond",
        "-o",
        "/tmp/" + uid,
        ly_file
    ]


    r = subprocess.run(
        lilypond,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )


    if r.returncode != 0:

        print(r.stderr)

        raise Exception(
            "lilypond failed"
        )



    generated_pdf = "/tmp/" + uid + ".pdf"


    return generated_pdf