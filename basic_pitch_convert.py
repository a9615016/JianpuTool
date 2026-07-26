import sys
import os

from basic_pitch.inference import predict_and_save
from basic_pitch import ICASSP_2022_MODEL_PATH


if len(sys.argv) < 3:
    print("usage: python basic_pitch_convert.py input.mp3 output.mid")
    exit(1)


input_audio = sys.argv[1]
output_mid = sys.argv[2]


print("開始 BasicPitch")
print("輸入:", input_audio)


output_dir = os.path.dirname(output_mid)


predict_and_save(
    [input_audio],
    output_dir,
    True,                  # save_midi
    True,                  # sonify_midi
    True,                  # save_model_outputs
    True,                  # save_notes
    ICASSP_2022_MODEL_PATH
)


# BasicPitch輸出的檔名
generated = os.path.join(
    output_dir,
    os.path.splitext(
        os.path.basename(input_audio)
    )[0] + ".mid"
)


if os.path.exists(generated):

    os.rename(
        generated,
        output_mid
    )


print("MIDI完成:")
print(output_mid)