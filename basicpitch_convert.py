import sys
import os
import traceback


def check_input_audio(audio_path):
    """
    在呼叫 BasicPitch 之前先驗證輸入檔案本身沒問題，
    避免真正的錯誤原因被 basic_pitch 內部的例外訊息蓋掉、看不清楚。
    """

    if not os.path.isfile(audio_path):
        raise FileNotFoundError(f"找不到輸入音檔: {audio_path}")

    size = os.path.getsize(audio_path)

    if size == 0:
        raise ValueError(
            f"輸入音檔是空檔(0 bytes)，通常代表上一步(Demucs 人聲分離)"
            f"沒有正確產生檔案: {audio_path}"
        )

    print(f"[BasicPitch] 輸入檔案: {audio_path} ({size} bytes)")

    # 嘗試用 soundfile 讀取檔頭，確認是合法的音檔格式，
    # 而不是等到丟進模型才因為格式問題整個掛掉、卻只印出很難懂的錯誤。
    try:
        import soundfile as sf
        info = sf.info(audio_path)
        print(
            f"[BasicPitch] 音檔資訊: "
            f"{info.samplerate}Hz, {info.channels}ch, "
            f"{info.duration:.1f}秒, 格式={info.format}"
        )

    except Exception as e:
        raise ValueError(
            f"輸入音檔無法被讀取，可能格式損毀或不是合法的音訊檔: {audio_path}\n"
            f"原始錯誤: {e}"
        )


def convert(audio, output):

    print("[BasicPitch] 開始處理:", audio)

    check_input_audio(audio)

    try:
        from basic_pitch.inference import predict
        from basic_pitch import ICASSP_2022_MODEL_PATH

    except Exception as e:
        print("[BasicPitch] 匯入 basic_pitch 套件失敗，請確認已安裝:")
        print("    pip install basic-pitch")
        traceback.print_exc()
        raise

    try:
        model_output = predict(
            audio,
            ICASSP_2022_MODEL_PATH,
            onset_threshold=0.55,        # 提高可減少誤判的音符起點(雜音)
            frame_threshold=0.35,        # 音高存在的信心門檻,提高可過濾微弱雜訊
            minimum_note_length=80,    # 單位ms,過濾掉太短的雜訊音符
            minimum_frequency=130.0,    # 約C3,過濾掉低於人聲音域的雜訊
            maximum_frequency=1050.0,   # 約C6,過濾掉超出人聲音域的高頻雜訊
            multiple_pitch_bends=False,
            melodia_trick=True          # 開啟旋律優先演算法,較適合單旋律人聲
        )

    except Exception as e:
        print("[BasicPitch] predict() 執行失敗，完整錯誤如下:")
        traceback.print_exc()
        raise

    midi = model_output[1]

    if midi is None:
        raise RuntimeError("[BasicPitch] predict() 沒有回傳有效的 MIDI 物件")

    midi.write(output)

    if not os.path.isfile(output) or os.path.getsize(output) == 0:
        raise RuntimeError(f"[BasicPitch] 輸出的 MIDI 是空檔或未產生: {output}")

    print("[BasicPitch] 完成 ->", output)


if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("用法: python basicpitch_convert.py input.wav output.mid")
        sys.exit(1)

    try:
        convert(sys.argv[1], sys.argv[2])

    except Exception:
        # 確保任何錯誤都完整印出來(而不是被吃掉只剩 exit code 1),
        # 這樣 pipeline.py 捕捉到的 stdout 裡才會有真正的原因。
        traceback.print_exc()
        sys.exit(1)
