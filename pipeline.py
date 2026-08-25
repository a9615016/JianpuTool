import os
import subprocess
import sys
import traceback


# ============================================================
# JianpuTool Professional MVP 3.0
#
# Pipeline
#
# MP3/WAV
#   ↓
# 1 Demucs
#   ↓
# 2 BasicPitch
#   ↓
# 3 BPM + Key
#   ↓
# 4 Melody Clean + Quantize
#   ↓
# 5 MIDI -> MusicXML
#   ↓
# 6 MusicXML Duration Fix
#   ↓
# 7 MusicXML -> Jianpu PDF
#
# 特點：
# - Windows / Linux / Streamlit Cloud
# - UTF-8
# - 完整 stdout/stderr
# - 明確錯誤定位
# - 每一步檢查輸出檔案
# ============================================================


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
# 顯示標題
# ============================================================

def print_header(title):

    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


# ============================================================
# 檢查檔案
# ============================================================

def check_file(path, description):

    if not os.path.isfile(path):

        raise RuntimeError(
            f"{description}產生失敗：\n"
            f"{path}"
        )

    size = os.path.getsize(path)

    if size <= 0:

        raise RuntimeError(
            f"{description}是空檔案：\n"
            f"{path}"
        )

    print(
        f"✅ {description}"
    )

    print(
        f"   路徑：{path}"
    )

    print(
        f"   大小：{size:,} bytes"
    )


# ============================================================
# 執行單一步驟
# ============================================================

def run_step(
    step_name,
    script,
    *args
):

    print_header(step_name)

    script_path = os.path.join(
        BASE_DIR,
        script
    )

    # --------------------------------------------------------
    # 檢查 Python script
    # --------------------------------------------------------

    if not os.path.isfile(script_path):

        raise FileNotFoundError(
            f"找不到程式：\n"
            f"{script_path}"
        )

    # --------------------------------------------------------
    # 建立 command
    # --------------------------------------------------------

    cmd = [
        PYTHON,
        script_path,
        *[
            str(x)
            for x in args
        ]
    ]

    # --------------------------------------------------------
    # UTF-8 environment
    # --------------------------------------------------------

    env = os.environ.copy()

    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"

    # --------------------------------------------------------
    # 顯示 command
    # --------------------------------------------------------

    print("執行指令：")

    print(
        " ".join(
            f'"{x}"' if " " in x else x
            for x in cmd
        )
    )

    print()

    # --------------------------------------------------------
    # 執行
    # --------------------------------------------------------

    try:

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env
        )

    except Exception as e:

        print()
        print("❌ subprocess 執行例外")
        print(str(e))

        raise RuntimeError(
            f"[{step_name}] subprocess 執行失敗：{e}"
        ) from e

    # --------------------------------------------------------
    # 完整輸出
    # --------------------------------------------------------

    output = result.stdout or ""

    print(output)

    # --------------------------------------------------------
    # 成功
    # --------------------------------------------------------

    if result.returncode == 0:

        print()
        print(
            f"✅ {step_name} 成功"
        )

        return output

    # --------------------------------------------------------
    # 失敗
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print(
        f"❌ {step_name} 失敗"
    )
    print(
        f"Exit code: {result.returncode}"
    )
    print("=" * 70)

    raise RuntimeError(
        f"\n"
        f"[{step_name}] 執行失敗\n\n"
        f"Exit code: {result.returncode}\n\n"
        f"Command:\n"
        f"{' '.join(cmd)}\n\n"
        f"----- 程式完整輸出 -----\n"
        f"{output}"
    )


# ============================================================
# 完整 Pipeline
# ============================================================

def convert_pipeline(
    input_audio,
    workdir
):

    print_header(
        "🎵 JianpuTool Professional MVP 3.0"
    )

    print(
        "完整 MP3/WAV → 數字簡譜 PDF Pipeline"
    )

    print()

    # ========================================================
    # 路徑
    # ========================================================

    input_audio = os.path.abspath(
        input_audio
    )

    workdir = os.path.abspath(
        workdir
    )

    os.makedirs(
        workdir,
        exist_ok=True
    )

    print(
        f"Python：{PYTHON}"
    )

    print(
        f"BASE_DIR：{BASE_DIR}"
    )

    print(
        f"Input：{input_audio}"
    )

    print(
        f"Workdir：{workdir}"
    )

    # ========================================================
    # Input
    # ========================================================

    if not os.path.isfile(input_audio):

        raise FileNotFoundError(
            f"找不到輸入音檔：\n"
            f"{input_audio}"
        )

    input_size = os.path.getsize(
        input_audio
    )

    print(
        f"輸入檔案大小："
        f"{input_size:,} bytes"
    )

    # ========================================================
    # 1. Demucs
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
        "人聲 WAV"
    )

    # ========================================================
    # 2. BasicPitch
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
    # 3. BPM + Key
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

    if os.path.isfile(info_json):

        check_file(
            info_json,
            "info.json"
        )

    else:

        print(
            "⚠ key_detect.py 沒有產生 info.json"
        )

        print(
            "⚠ 後續將使用預設 C major"
        )

    # ========================================================
    # 4. Melody Clean
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
    # 5. MIDI -> MusicXML
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
    # 6. Duration Fix
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
    # 7. Jianpu PDF
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

    print_header(
        "🎉🎉🎉 完整轉換成功 🎉🎉🎉"
    )

    print(
        f"📥 Input：{input_audio}"
    )

    print(
        f"🎤 Vocals：{vocals}"
    )

    print(
        f"🎹 MIDI：{clean_midi}"
    )

    print(
        f"🎼 MusicXML：{fixed_musicxml}"
    )

    print(
        f"📄 PDF：{pdf}"
    )

    print()

    return pdf


# ============================================================
# CMD
# ============================================================

if __name__ == "__main__":

    if len(sys.argv) < 3:

        print()
        print(
            "JianpuTool Pipeline"
        )
        print()

        print(
            'python pipeline.py '
            '"input.mp3" '
            '"outputs/song"'
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
        print("=" * 70)
        print("❌ PIPELINE 失敗")
        print("=" * 70)
        print()

        print(
            str(e)
        )

        print()
        print("===== Traceback =====")

        traceback.print_exc()

        print()
        print("=" * 70)

        sys.exit(1)