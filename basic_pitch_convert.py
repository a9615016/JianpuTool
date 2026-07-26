import sys
import os

from basic_pitch.inference import predict_and_save
from basic_pitch import ICASSP_2022_MODEL_PATH


if len(sys.argv) < 3:
    print("usage: python basic_pitch_convert.py input.mp3 output.mid")
    exit(1)


input_audio = sys.argv[1]
output_dir = os.path.dirname(sys.argv[2])

filename = os.path.basename(
    sys.argv[2]
)


print("BasicPitch input:")
print(input_audio)


predict_and_save(
    [input_audio],
    output_dir,
    True,
    True,
    True,
    ICASSP_2022_MODEL_PATH
)


# BasicPitch 預設輸出名稱
generated = os.path.join(
    output_dir,
    os.path.splitext(
        os.path.basename(input_audio)
    )[0] + ".mid"
)


target = sys.argv[2]


if os.path.exists(generated):
    os.rename(
        generated,
        target
    )


print("MIDI完成:")
print(target)