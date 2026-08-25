"""
JianpuTool - MP3/WAV -> 數字簡譜 PDF
完整 6 步驟 Pipeline
"""

import os
import subprocess
import sys


# ============================================================
# 基本設定
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

PYTHON = sys.executable


# ============================================================
# 執行單一步驟
# ============================================================

def run_step(step_name, script, *args):
    print()
    print("=" * 60)
    print(step_name)
    print("=" * 60)

    script_path = os.path.join(BASE_DIR, script)

    if not os.path.exists(script_path):
        raise FileNotFoundError(
            f"找不到程式：{script_path}"
        )

    cmd = [PYTHON, script_path, *args]

    env = os.environ.copy()

    # Windows UTF-8
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"

    print("執行：")
    print(" ".join(f'"{x}"' if " " in x else x for x in cmd))
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

    print(result.stdout)

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
# 完整 MP3/WAV -> Jianpu PDF
# ============================================================

def convert_pipeline(input_audio, workdir):
    """
    完整轉換流程：

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
    [3] BPM + 調性偵測
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
    [6] MusicXML -> 數字簡譜 PDF
       ↓
    jianpu.pdf
    """

    os.makedirs(workdir, exist_ok=True)

    input_audio = os.path.abspath(input_audio)
    workdir = os.path.abspath(workdir)

    if not os.path.exists(input_audio):
        raise FileNotFoundError(
            f"找不到輸入音檔：{input_audio}"
        )

    print()
    print("=" * 60)
    print("JianpuTool 完整自動轉換")
    print("=" * 60)
    print(f"輸入音檔：{input_audio}")
    print(f"工作目錄：{workdir}")
    print("=" * 60)


    # ========================================================
    # [1/6] Demucs 人聲分離
    # ========================================================

    vocals = os.path.join(
        workdir,
        "vocals.wav"
    )

    run_step(
        "1/6 Demucs 人聲分離",
        "demucs_extract.py",
        input_audio,
        vocals
    )

    if not os.path.exists(vocals):
        raise RuntimeError(
            f"Demucs 執行完成，但是找不到：{vocals}"
        )

    print(f"✅ 人聲檔案：{vocals}")


    # ========================================================
    # [2/6] BasicPitch
    # ========================================================

    raw_midi = os.path.join(
        workdir,
        "raw_melody.mid"
    )

    run_step(
        "2/6 BasicPitch 旋律辨識",
        "basicpitch_convert.py",
        vocals,
        raw_midi
    )

    if not os.path.exists(raw_midi):
        raise RuntimeError(
            f"BasicPitch 執行完成，但是找不到：{raw_midi}"
        )

    print(f"✅ MIDI：{raw_midi}")


    # ========================================================
    # [3/6] BPM + 調性偵測
    # ========================================================

    info_json = os.path.join(
        workdir,
        "info.json"
    )

    run_step(
        "3/6 BPM + 調性偵測",
        "key_detect.py",
        input_audio,
        raw_midi,
        info_json
    )

    if os.path.exists(info_json):
        print(f"✅ info.json：{info_json}")
    else:
        print("⚠ key_detect 沒有產生 info.json")


    # ========================================================
    # [4/6] 旋律清理 + 量化
    # ========================================================

    clean_midi = os.path.join(
        workdir,
        "clean_melody.mid"
    )

    run_step(
        "4/6 精準旋律清理 + 量化",
        "melody_clean_quantize.py",
        raw_midi,
        clean_midi,
        info_json
    )

    if not os.path.exists(clean_midi):
        raise RuntimeError(
            f"旋律清理完成，但是找不到：{clean_midi}"
        )

    print(f"✅ 清理後 MIDI：{clean_midi}")


    # ========================================================
    # [5/6] MIDI -> MusicXML
    # ========================================================

    musicxml = os.path.join(
        workdir,
        "final.musicxml"
    )

    run_step(
        "5/6 MIDI -> MusicXML",
        "midi_to_musicxml.py",
        clean_midi,
        musicxml,
        info_json
    )

    if not os.path.exists(musicxml):
        raise RuntimeError(
            f"MusicXML 產生完成，但是找不到：{musicxml}"
        )

    print(f"✅ MusicXML：{musicxml}")


    # ========================================================
    # [6/6] MusicXML -> 數字簡譜 PDF
    # ========================================================

    pdf = os.path.join(
        workdir,
        "jianpu.pdf"
    )

    run_step(
        "6/6 MusicXML -> 數字簡譜 PDF",
        "jianpu_pdf.py",
        musicxml,
        pdf
    )

    if not os.path.exists(pdf):
        raise RuntimeError(
            f"LilyPond 執行完成，但是找不到 PDF：{pdf}"
        )

    print()
    print("=" * 60)
    print("🎉 完整轉換成功")
    print("=" * 60)
    print(f"📄 數字簡譜 PDF：{pdf}")
    print("=" * 60)

    return pdf


# ============================================================
# 命令列模式
# ============================================================

if __name__ == "__main__":

    if len(sys.argv) < 3:
        print()
        print("使用方法：")
        print()
        print(
            'python pipeline.py "C.mp3" "outputs\\C"'
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
        print("✅ Pipeline 完成")
        print(f"PDF = {pdf}")

    except Exception as e:
        print()
        print("=" * 60)
        print("❌ Pipeline 失敗")
        print("=" * 60)
        print(str(e))
        print("=" * 60)
        sys.exit(1)