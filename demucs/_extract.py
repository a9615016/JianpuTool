import sys
from pathlib import Path

import torch
import soundfile as sf

from demucs.pretrained import get_model
from demucs.apply import apply_model
from demucs.audio import AudioFile, convert_audio


def main():

    if len(sys.argv) != 3:
        print("=" * 40)
        print("用法:")
        print(
            'python demucs\\_extract.py "輸入.mp3" "輸出_vocals.wav"'
        )
        print("=" * 40)
        sys.exit(1)

    input_audio = Path(sys.argv[1]).resolve()
    output_audio = Path(sys.argv[2]).resolve()

    if not input_audio.exists():
        print(f"❌ 找不到輸入檔案:")
        print(input_audio)
        sys.exit(1)

    output_audio.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    print("=" * 40)
    print("開始 Demucs 人聲分離")
    print("=" * 40)

    print(f"輸入: {input_audio}")
    print(f"輸出: {output_audio}")
    print()

    try:

        # --------------------------------------------------
        # 1. 載入 Demucs
        # --------------------------------------------------

        print("載入 Demucs 模型: htdemucs")

        model = get_model("htdemucs")

        model.cpu()
        model.eval()

        print("✅ Demucs 模型載入成功")
        print()

        # --------------------------------------------------
        # 2. 讀取音訊
        # --------------------------------------------------

        print("讀取音訊...")

        wav = AudioFile(str(input_audio)).read(
            streams=0,
            samplerate=model.samplerate,
            channels=model.audio_channels
        )

        # 確保音訊格式符合模型要求
        wav = convert_audio(
            wav,
            model.samplerate,
            model.samplerate,
            model.audio_channels
        )

        print(f"取樣率: {model.samplerate}")
        print(f"聲道數: {model.audio_channels}")
        print(f"音訊長度: {wav.shape[-1] / model.samplerate:.2f} 秒")
        print()

        # --------------------------------------------------
        # 3. 加入 batch 維度
        # --------------------------------------------------

        wav = wav.unsqueeze(0)

        # --------------------------------------------------
        # 4. Demucs 人聲分離
        # --------------------------------------------------

        print("開始 Demucs 人聲分離...")
        print("CPU 模式")
        print()

        with torch.no_grad():

            sources = apply_model(
                model,
                wav,
                device="cpu",
                shifts=1,
                split=True,
                overlap=0.25,
                progress=True
            )

        print()
        print("✅ Demucs 分離完成")
        print()

        # --------------------------------------------------
        # 5. 找 vocals
        # --------------------------------------------------

        print("Demucs sources:")

        for i, source in enumerate(model.sources):
            print(f"  [{i}] {source}")

        print()

        vocals_index = model.sources.index("vocals")

        vocals = sources[0, vocals_index]

        # --------------------------------------------------
        # 6. Tensor → NumPy
        # --------------------------------------------------

        vocals = vocals.cpu().numpy()

        # Demucs:
        #
        # [channels, samples]
        #
        # soundfile:
        #
        # [samples, channels]
        #
        vocals = vocals.T

        # --------------------------------------------------
        # 7. 用 soundfile 寫 WAV
        #
        # 重要：
        # 不使用 torchaudio.save()
        # 不使用 TorchCodec
        # --------------------------------------------------

        print("正在寫出 vocals.wav...")

        sf.write(
            str(output_audio),
            vocals,
            model.samplerate,
            subtype="PCM_16"
        )

        # --------------------------------------------------
        # 8. 確認檔案
        # --------------------------------------------------

        if not output_audio.exists():

            print()
            print("❌ WAV 檔案沒有產生")
            sys.exit(1)

        file_size = output_audio.stat().st_size

        if file_size <= 0:

            print()
            print("❌ WAV 檔案大小為 0")
            sys.exit(1)

        print()
        print("=" * 40)
        print("✅ Demucs 人聲分離成功")
        print("=" * 40)

        print(f"輸出檔案:")
        print(output_audio)

        print(f"檔案大小: {file_size:,} bytes")

        print()
        print("下一步可以直接把 vocals.wav")
        print("送給 BasicPitch。")

    except Exception as e:

        print()
        print("=" * 40)
        print("❌ Demucs 人聲分離失敗")
        print("=" * 40)

        print(f"{type(e).__name__}: {e}")

        import traceback

        traceback.print_exc()

        sys.exit(1)


if __name__ == "__main__":
    main()