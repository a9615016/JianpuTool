import subprocess
import sys
import os


def extract_vocal(mp3, output):

    cmd = [
        "demucs",
        "--two-stems=vocals",
        "-o",
        "separated",
        mp3
    ]

    subprocess.run(cmd, check=True)


    name = os.path.splitext(os.path.basename(mp3))[0]

    vocals = os.path.join(
        "separated",
        "htdemucs",
        name,
        "vocals.wav"
    )


    if not os.path.exists(vocals):
        raise Exception("Demucs 沒產生 vocals.wav")


    os.rename(vocals, output)


if __name__ == "__main__":

    extract_vocal(
        sys.argv[1],
        sys.argv[2]
    )