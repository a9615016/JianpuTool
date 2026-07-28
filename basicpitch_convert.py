import sys
import os
import logging

from basic_pitch.inference import predict_and_save
from basic_pitch import ICASSP_2022_MODEL_PATH


logging.basicConfig(level=logging.INFO)


def convert_audio_to_midi(input_audio, output_midi):

    print("====================")
    print("開始 BasicPitch")
    print("輸入:", input_audio)

    if not os.path.exists(input_audio):
        raise FileNotFoundError(input_audio)


    output_dir = os.path.dirname(output_midi)

    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)


    print("Predicting MIDI...")


    predict_and_save(
        [input_audio],
        output_directory=output_dir,
        save_midi=True,
        sonify_midi=False,
        save_model_outputs=False,
        model_or_model_path=ICASSP_2022_MODEL_PATH
    )


    # BasicPitch 預設名稱
    generated = os.path.join(
        output_dir,
        os.path.splitext(
            os.path.basename(input_audio)
        )[0] + ".mid"
    )


    if os.path.exists(generated):

        os.rename(
            generated,
            output_midi
        )

    else:
        # 某些版本輸出 midi
        mids = [
            f for f in os.listdir(output_dir)
            if f.endswith(".mid")
        ]

        if len(mids) == 0:
            raise Exception(
                "BasicPitch 沒有產生 MIDI"
            )

        os.rename(
            os.path.join(output_dir, mids[0]),
            output_midi
        )


    print("MIDI完成:", output_midi)



if __name__ == "__main__":

    if len(sys.argv) < 3:
        print(
            "用法: python basicpitch_convert.py input.mp3 output.mid"
        )
        sys.exit(1)


    input_audio = sys.argv[1]
    output_midi = sys.argv[2]


    convert_audio_to_midi(
        input_audio,
        output_midi
    )