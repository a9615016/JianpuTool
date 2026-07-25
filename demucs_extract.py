import subprocess
import sys
import os
import shutil


def extract_vocal(mp3, output):

    print("開始 Demucs")
    print("輸入:", mp3)


    workdir = os.path.dirname(output)


    separated = os.path.join(
        workdir,
        "separated"
    )


    cmd = [

        "demucs",

        "-n",
        "htdemucs",

        "--two-stems=vocals",

        "-o",
        separated,

        mp3

    ]


    result = subprocess.run(

        cmd,

        stdout=subprocess.PIPE,

        stderr=subprocess.STDOUT,

        text=True

    )


    print(result.stdout)


    if result.returncode != 0:

        raise Exception(
            result.stdout
        )


    name = os.path.splitext(
        os.path.basename(mp3)
    )[0]


    vocals = os.path.join(

        separated,

        "htdemucs",

        name,

        "vocals.wav"

    )


    if not os.path.exists(vocals):

        raise Exception(
            "Demucs 沒產生 vocals.wav\n"
            + vocals
        )


    shutil.move(
        vocals,
        output
    )


    print(
        "完成:",
        output
    )