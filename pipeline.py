import os
import subprocess
import sys


# ============================================================
# 基本設定
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "outputs"
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

PYTHON = sys.executable


# ============================================================
# 執行單一步驟
# ============================================================

def run_step(
    step_name,
    script,
    *args
):

    print()
    print("=" * 60)
    print(step_name)
    print("=" * 60)

    script_path = os.path.join(
        BASE_DIR,
        script
    )

    if not os.path.isfile(
        script_path
    ):
        raise FileNotFoundError(
            f"找不到程式：{script_path}"
        )

    cmd = [
        PYTHON,
        script_path,
        *args
    ]

    env = os.environ.copy()

    # --------------------------------------------------------
    # Windows / Linux UTF-8
    # --------------------------------------------------------

    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"

    print("執行：")

    print(
        " ".join(
            f'"{x}"' if " " in x else x
            for x in cmd
        )
    )

    print()

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env
    )

    print(
        result.stdout
    )

    if result.returncode != 0:

        raise RuntimeError(
            f"\n[{step_name}] 執行失敗\n"
            f"Exit code: {result.returncode}\n"
            f"Command: {' '.join(cmd)}\n\n"
            f"----- 程式輸出 -----\n"
            f"{result.stdout}"
        )

    return result.stdout


# ============================================================
# 檢查檔案
# ============================================================

def check_file(
    path,
    description
):

    if not os.path.isfile(path):

        raise RuntimeError(
            f"{description}產生失敗：\n"
            f"{path}"
        )

    size = os.path.getsize(
        path
    )

    if size <= 0:

        raise RuntimeError(
            f"{description}是空檔案：\n"
            f"{path}"
        )

    print(
        f"✅ {description}："
        f"{path}"
    )

    print(
        f"   檔案大小：{size:,} bytes"
    )


# ============================================================
# 完整轉換
# ============================================================

def convert_pipeline(
    input_audio,
    workdir
):

    """
    MP3/WAV
       ↓
    [1] Demucs
       ↓
    vocals.wav
       ↓
    [2] BasicPitch
       ↓
    raw_melody.mid
       ↓
    [3] BPM + 調性
       ↓
    info.json
       ↓
    [4] 旋律清理 + 量化
       ↓
    clean_melody.mid
       ↓
    [5] MIDI -> MusicXML
       ↓
    final.musicxml
       ↓
    [6] Duration Fix
       ↓
    final_fixed.musicxml
       ↓
    [7] jianpu-ly + LilyPond
       ↓
    jianpu.pdf
    """

    # ========================================================
    # 工作目錄
    # ========================================================

    os.makedirs(
        workdir,
        exist_ok=True
    )

    input_audio = os.path.abspath(
        input_audio
    )

    workdir = os.path.abspath(
        workdir
    )

    # ========================================================
    # 檢查輸入
    # ========================================================

    if not os.path.isfile(
        input_audio
    ):

        raise FileNotFoundError(
            f"找不到輸入音檔："
            f"{input_audio}"
        )

    # ========================================================
    # 開始
    # ========================================================

    print()

    print("=" * 60)
    print("JianpuTool 完整 7 步驟自動轉換")
    print("=" * 60)

    print(
        f"輸入音檔：{input_audio}"
    )

    print(
        f"工作目錄：{workdir}"
    )

    print("=" * 60)


    # ========================================================
    # [1/7] Demucs
    # ========================================================

    vocals = os.path.join(
        workdir,
        "vocals.wav"
    )

    run_step(
        "1/7 Demucs 人聲分離",
        "demucs_extract.py",
        input_audio,
        vocals
    )

    check_file(
        vocals,
        "人聲檔案"
    )


    # ========================================================
    # [2/7] BasicPitch
    # ========================================================

    raw_midi = os.path.join(
        workdir,
        "raw_melody.mid"
    )

    run_step(
        "2/7 BasicPitch 旋律辨識",
        "basicpitch_convert.py",
        vocals,
        raw_midi
    )

    check_file(
        raw_midi,
        "原始 MIDI"
    )


    # ========================================================
    # [3/7] BPM + 調性
    # ========================================================

    info_json = os.path.join(
        workdir,
        "info.json"
    )

    run_step(
        "3/7 BPM + 調性偵測",
        "key_detect.py",
        input_audio,
        raw_midi,
        info_json
    )

    if os.path.isfile(
        info_json
    ):

        check_file(
            info_json,
            "info.json"
        )

    else:

        print(
            "⚠ key_detect 沒有產生 info.json"
        )

        print(
            "⚠ 後續將使用預設調性"
        )


    # ========================================================
    # [4/7] 旋律清理 + 量化
    # ========================================================

    clean_midi = os.path.join(
        workdir,
        "clean_melody.mid"
    )

    run_step(
        "4/7 精準旋律清理 + 量化",
        "melody_clean_quantize.py",
        raw_midi,
        clean_midi,
        info_json
    )

    check_file(
        clean_midi,
        "清理後 MIDI"
    )


    # ========================================================
    # [5/7] MIDI -> MusicXML
    # ========================================================

    musicxml = os.path.join(
        workdir,
        "final.musicxml"
    )

    run_step(
        "5/7 MIDI -> MusicXML",
        "midi_to_musicxml.py",
        clean_midi,
        musicxml,
        info_json
    )

    check_file(
        musicxml,
        "原始 MusicXML"
    )


    # ========================================================
    # [6/7] MusicXML Duration Fix
    # ========================================================

    fixed_musicxml = os.path.join(
        workdir,
        "final_fixed.musicxml"
    )

    run_step(
        "6/7 MusicXML Duration Fix",
        "musicxml_duration_fix.py",
        musicxml,
        fixed_musicxml
    )

    check_file(
        fixed_musicxml,
        "修正後 MusicXML"
    )


    # ========================================================
    # [7/7] MusicXML -> 數字簡譜 PDF
    # ========================================================

    pdf = os.path.join(
        workdir,
        "jianpu.pdf"
    )

    run_step(
        "7/7 MusicXML -> 數字簡譜 PDF",
        "jianpu_pdf.py",
        fixed_musicxml,
        pdf
    )

    check_file(
        pdf,
        "數字簡譜 PDF"
    )


    # ========================================================
    # 完成
    # ========================================================

    print()

    print("=" * 60)
    print("🎉🎉🎉 完整轉換成功 🎉🎉🎉")
    print("=" * 60)

    print(
        f"📥 輸入：{input_audio}"
    )

    print(
        f"🎵 人聲：{vocals}"
    )

    print(
        f"🎹 MIDI：{clean_midi}"
    )

    print(
        f"🎼 MusicXML：{fixed_musicxml}"
    )

    print(
        f"📄 數字簡譜 PDF：{pdf}"
    )

    print("=" * 60)

    return pdf


# ============================================================
# CMD
# ============================================================

if __name__ == "__main__":

    if len(sys.argv) < 3:

        print()

        print(
            "JianpuTool 使用方法："
        )

        print()

        print(
            'python pipeline.py '
            '"C:\\music\\song.mp3" '
            '"outputs\\song"'
        )

        print()

        print(
            "例如："
        )

        print(
            'python pipeline.py '
            '"C:\\Users\\user\\Desktop\\JianpuTool\\C.mp3" '
            '"outputs\\C"'
        )

        print()

        sys.exit(1)


    input_audio = sys.argv[1]

    workdir = sys.argv[2]


    try:

        pdf = convert_pipeline(
            input_audio,
            workdir
        )

        print()

        print(
            "✅ Pipeline 完成"
        )

        print(
            f"PDF = {pdf}"
        )

    except Exception as e:

        print()

        print("=" * 60)
        print("❌ Pipeline 失敗")
        print("=" * 60)

        print(
            str(e)
        )

        print("=" * 60)

        sys.exit(1)