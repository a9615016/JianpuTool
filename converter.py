import os
import subprocess
import glob
import shutil


LILYPOND = r"C:\lilypond-2.26.0\bin\lilypond.exe"


def convert_musicxml(musicxml_file):

    print("==============================")
    print("開始轉換")
    print(musicxml_file)
    print("==============================")


    base = os.path.splitext(
        os.path.basename(musicxml_file)
    )[0]


    folder = os.path.dirname(
        musicxml_file
    )


    ly_file = os.path.join(
        folder,
        base + "_jianpu.ly"
    )


    pdf_file = os.path.join(
        folder,
        base + ".pdf"
    )


    #
    # 1. MusicXML → LilyPond
    #
    print("產生 LilyPond 檔...")


    cmd = [
        "python",
        "-m",
        "jianpu_ly",
        musicxml_file
    ]


    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore"
    )


    print(result.stdout)
    print(result.stderr)


    #
    # jianpu_ly 新版會輸出 Temp
    #
    temp_files = glob.glob(
        os.path.join(
            os.environ["TEMP"],
            "*.ly"
        )
    )


    newest = None

    if temp_files:

        newest = max(
            temp_files,
            key=os.path.getmtime
        )


    if newest and os.path.getsize(newest) > 0:

        shutil.copy(
            newest,
            ly_file
        )

    else:

        # 舊版 fallback
        with open(
            ly_file,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                result.stdout
            )


    if not os.path.exists(ly_file):

        raise Exception(
            "沒有產生 LilyPond 檔"
        )


    print(
        "完成:",
        ly_file
    )


    #
    # 2. LilyPond → PDF
    #
    print("開始產生 PDF...")


    subprocess.run(
        [
            LILYPOND,
            "-o",
            os.path.join(folder, base),
            ly_file
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore"
    )


    if not os.path.exists(pdf_file):

        raise Exception(
            "沒有產生 PDF"
        )


    print(
        "完成 PDF:",
        pdf_file
    )


    return pdf_file