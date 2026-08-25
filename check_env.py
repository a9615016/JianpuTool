import sys
import os
import shutil
import traceback
import subprocess


OK = "OK"
FAIL = "FAIL"
OPTIONAL = "OPTIONAL"

results = []


def record(name, passed, message=""):
    results.append((name, passed, message))

    mark = OK if passed else FAIL
    print(f"[{mark}] {name}")

    if message:
        for line in message.splitlines():
            print(f"    {line}")


def record_optional(name, message=""):
    print(f"[{OPTIONAL}] {name}")

    if message:
        for line in message.splitlines():
            print(f"    {line}")


# ============================================================
# 1. Python
# ============================================================

def check_python_version():
    v = sys.version_info

    ok = (
        v.major == 3
        and 8 <= v.minor <= 11
    )

    message = f"目前版本: {sys.version.split()[0]}"

    if not ok:
        message += "\n建議使用 Python 3.8 ~ 3.11"

    record(
        "Python 版本",
        ok,
        message
    )


# ============================================================
# 2. 必要套件
# ============================================================

def check_import(name, import_name=None, pip_name=None):
    import_name = import_name or name
    pip_name = pip_name or name

    try:
        __import__(import_name)

        record(
            f"套件: {name}",
            True
        )

        return True

    except Exception as e:

        record(
            f"套件: {name}",
            False,
            f"匯入失敗: {e}\n"
            f"修復: python -m pip install {pip_name}"
        )

        return False


# ============================================================
# 3. 選配套件
# ============================================================

def check_import_optional(name, import_name=None):
    import_name = import_name or name

    try:
        __import__(import_name)

        record_optional(
            f"套件: {name}",
            "已安裝"
        )

    except Exception:
        record_optional(
            f"套件: {name}",
            "未安裝，但不影響目前 BasicPitch 0.4.0 的推論"
        )


# ============================================================
# 4. 外部工具
# ============================================================

def check_command(name, command, version_arg="--version"):

    path = shutil.which(command)

    if path is None:
        record(
            f"外部工具: {name}",
            False,
            f"找不到指令: {command}\n"
            f"請確認已安裝並加入 PATH"
        )

        return False

    try:
        result = subprocess.run(
            [command, version_arg],
            capture_output=True,
            text=True,
            timeout=15
        )

        output = (
            result.stdout
            or result.stderr
            or ""
        ).strip()

        lines = output.splitlines()

        first_line = (
            lines[0]
            if lines
            else "(無版本輸出)"
        )

        record(
            f"外部工具: {name}",
            True,
            f"路徑: {path}\n{first_line}"
        )

        return True

    except Exception as e:

        record(
            f"外部工具: {name}",
            False,
            f"執行失敗: {e}"
        )

        return False


# ============================================================
# 5. BasicPitch 實際推論
# ============================================================

def check_basic_pitch_runtime():

    print()
    print("正在實際測試 BasicPitch 模型推論...")
    print("請稍候...")

    tmp_wav = os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)
        ),
        "_env_test.wav"
    )

    try:

        import numpy as np
        import soundfile as sf

        sr = 22050

        t = np.linspace(
            0,
            2.0,
            int(sr * 2.0),
            endpoint=False
        )

        y = (
            0.3
            * np.sin(
                2 * np.pi * 440 * t
            )
        )

        sf.write(
            tmp_wav,
            y,
            sr
        )

        from basic_pitch.inference import predict
        from basic_pitch import ICASSP_2022_MODEL_PATH

        model_output = predict(
            tmp_wav,
            ICASSP_2022_MODEL_PATH
        )

        midi = model_output[1]

        if midi is None:
            raise RuntimeError(
                "BasicPitch 沒有產生 MIDI"
            )

        record(
            "BasicPitch 實際推論測試",
            True,
            "模型可以正常載入並產生 MIDI"
        )

        return True

    except Exception:

        record(
            "BasicPitch 實際推論測試",
            False,
            "執行失敗:\n"
            + traceback.format_exc()
        )

        return False

    finally:

        try:
            if os.path.exists(tmp_wav):
                os.remove(tmp_wav)
        except Exception:
            pass


# ============================================================
# 6. jianpu-ly
# ============================================================

def check_jianpu_ly_runtime():

    exe = shutil.which("jianpu-ly")

    if exe is None:

        record(
            "jianpu-ly 實際執行測試",
            False,
            "找不到 jianpu-ly\n"
            "修復: python -m pip install jianpu-ly"
        )

        return False

    try:

        subprocess.run(
            [exe, "--help"],
            capture_output=True,
            text=True,
            timeout=15
        )

        record(
            "jianpu-ly 實際執行測試",
            True,
            f"路徑: {exe}"
        )

        return True

    except Exception as e:

        record(
            "jianpu-ly 實際執行測試",
            False,
            f"執行失敗: {e}"
        )

        return False


# ============================================================
# 7. 主程式
# ============================================================

def main():

    print("========================================")
    print("JianpuTool 環境健檢")
    print("========================================")
    print()

    # Python
    check_python_version()

    print()

    # 必要套件
    check_import("fastapi")
    check_import("streamlit")
    check_import("numpy")
    check_import("mido")
    check_import("music21")
    check_import("librosa")
    check_import("soundfile")
    check_import(
        "basic_pitch",
        pip_name="basic-pitch"
    )
    check_import("demucs")

    # TensorFlow 是選配
    check_import_optional("tensorflow")

    print()

    # 外部工具
    check_command(
        "ffmpeg",
        "ffmpeg",
        "-version"
    )

    check_command(
        "LilyPond",
        "lilypond",
        "--version"
    )

    print()

    # jianpu-ly
    check_jianpu_ly_runtime()

    print()

    # BasicPitch 實際測試
    check_basic_pitch_runtime()

    # 結果
    print()
    print("========================================")
    print("健檢結果總覽")
    print("========================================")

    failed = [
        r for r in results
        if not r[1]
    ]

    for name, passed, message in results:
        print(
            f"[{OK if passed else FAIL}] {name}"
        )

    print()

    if not failed:

        print("🎉 所有必要項目全部通過！")
        print("✅ JianpuTool 環境基本完整")
        print("✅ 可以進一步測試 MP3 → MIDI → MusicXML → 簡譜 PDF")

    else:

        print(
            f"⚠ 有 {len(failed)} 項必要項目未通過。"
        )

        print(
            "請依照上面的修復建議處理。"
        )

        print(
            "修好之後重新執行:"
        )

        print(
            "python check_env.py"
        )


if __name__ == "__main__":
    main()