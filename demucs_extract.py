import os
import sys
import shutil
import subprocess
import tempfile
import glob

import torch
import soundfile as sf


# ============================================================
# Demucs 人聲分離
# 避免 torchaudio -> TorchCodec 相容性問題
#
# Demucs 負責：
#   MP3/WAV -> AI 人聲分離
#
# soundfile 負責：
#   Tensor -> WAV
#
# 不使用 torchaudio.save()
# 不使用 TorchCodec
# ============================================================


def patch_torchaudio_save():

    import torchaudio

    def safe_save(filepath, src, sample_rate, *args, **kwargs):

        print("[Demucs Safe Save] 使用 soundfile 寫入 WAV")
        print("[Demucs Safe Save] 輸出:", filepath)

        # Tensor -> numpy
        if hasattr(src, "detach"):
            audio = src.detach().cpu().numpy()
        else:
            audio = src

        # Demucs 通常是 [channels, samples]
        if audio.ndim == 2:
            audio = audio.T

        # 防止超出 [-1, 1]
        audio = audio.clip(-1.0, 1.0)

        sf.write(
            filepath,
            audio,
            sample_rate,
            subtype="PCM_16"
        )

        print("[Demucs Safe Save] 完成")

    torchaudio.save = safe_save

    print("[Demucs] 已套用 Safe Save")
    print("[Demucs] 不使用 TorchCodec")


def extract_vocal(input_audio, output_vocal):

    print("=" * 50)
    print("[1/6] Demucs 人聲分離")
    print("=" * 50)

    if not os.path.isfile(input_audio):
        raise Exception(f"找不到輸入音檔: {input_audio}")

    print("輸入:", input_audio)
    print("輸出:", output_vocal)

    # --------------------------------------------------------
    # 1. Monkey Patch torchaudio.save
    # --------------------------------------------------------

    patch_torchaudio_save()

    # --------------------------------------------------------
    # 2. 建立暫存資料夾
    # --------------------------------------------------------

    output_dir = os.path.dirname(output_vocal)

    if not output_dir:
        output_dir = "."

    os.makedirs(output_dir, exist_ok=True)

    temp_dir = os.path.join(
        output_dir,
        "_demucs_temp"
    )

    os.makedirs(temp_dir, exist_ok=True)

    # --------------------------------------------------------
    # 3. 呼叫 Demucs
    # --------------------------------------------------------

    cmd = [
        sys.executable,
        "-m",
        "demucs",

        "--two-stems=vocals",

        "-d",
        "cpu",

        "-o",
        temp_dir,

        input_audio
    ]

    print()
    print("[Demucs] 執行:")
    print(" ".join(f'"{x}"' if " " in x else x for x in cmd))
    print()

    # --------------------------------------------------------
    # 重要：
    #
    # 不能用 subprocess.run()
    # 因為 subprocess 會啟動新的 Python，
    # 我們前面的 torchaudio.save patch 不會傳過去。
    #
    # 所以改成直接 import Demucs。
    # --------------------------------------------------------

    import demucs.separate

    old_argv = sys.argv

    try:

        sys.argv = [
            "demucs",
            "--two-stems=vocals",
            "-d",
            "cpu",
            "-o",
            temp_dir,
            input_audio
        ]

        try:
            demucs.separate.main()

        except SystemExit as e:

            # Demucs 正常結束有時會呼叫 SystemExit(0)
            if e.code not in (None, 0):
                raise Exception(
                    f"Demucs 執行失敗，exit code={e.code}"
                )

    finally:

        sys.argv = old_argv

    # --------------------------------------------------------
    # 4. 搜尋 vocals.wav
    # --------------------------------------------------------

    print()
    print("[Demucs] 搜尋 vocals.wav ...")

    patterns = [
        os.path.join(
            temp_dir,
            "**",
            "vocals.wav"
        ),

        os.path.join(
            temp_dir,
            "**",
            "*vocals*.wav"
        )
    ]

    vocal_files = []

    for pattern in patterns:

        vocal_files.extend(
            glob.glob(
                pattern,
                recursive=True
            )
        )

    # 去除重複
    vocal_files = list(dict.fromkeys(vocal_files))

    if not vocal_files:

        print()
        print("[Demucs] 找不到 vocals.wav")

        print("[Demucs] 暫存資料夾內容:")

        for root, dirs, files in os.walk(temp_dir):

            for name in files:

                print(
                    os.path.join(
                        root,
                        name
                    )
                )

        raise Exception(
            "Demucs 已完成分離，但找不到 vocals.wav"
        )

    source_vocal = vocal_files[0]

    print("[Demucs] 找到:")
    print(source_vocal)

    # --------------------------------------------------------
    # 5. 複製到 pipeline 指定的位置
    # --------------------------------------------------------

    shutil.copy2(
        source_vocal,
        output_vocal
    )

    # --------------------------------------------------------
    # 6. 確認
    # --------------------------------------------------------

    if not os.path.isfile(output_vocal):

        raise Exception(
            "vocals.wav 複製失敗"
        )

    size = os.path.getsize(output_vocal)

    if size <= 0:

        raise Exception(
            "vocals.wav 是空檔案"
        )

    print()
    print("=" * 50)
    print("✅ Demucs 人聲分離成功")
    print("=" * 50)
    print("輸出:", output_vocal)
    print("大小:", size, "bytes")
    print()


if __name__ == "__main__":

    if len(sys.argv) != 3:

        print()
        print("用法:")
        print(
            "python demucs_extract.py "
            "input.mp3 output_vocal.wav"
        )
        print()

        sys.exit(1)

    input_audio = sys.argv[1]
    output_vocal = sys.argv[2]

    try:

        extract_vocal(
            input_audio,
            output_vocal
        )

    except Exception as e:

        print()
        print("=" * 50)
        print("❌ Demucs 人聲分離失敗")
        print("=" * 50)
        print(str(e))
        print()

        sys.exit(1)