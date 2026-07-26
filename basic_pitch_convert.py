import sys
import os

from basic_pitch.inference import (
    predict,
    Model
)

from basic_pitch import ICASSP_2022_MODEL_PATH


if len(sys.argv) < 3:
    print("usage: python basic_pitch_convert.py input.mp3 output.mid")
    exit(1)


input_file = sys.argv[1]
output_file = sys.argv[2]


print("BasicPitch input:")
print(input_file)


# 載入模型
model = Model(
    ICASSP_2022_MODEL_PATH
)


# 推論
model_output, midi_data, note_events = predict(
    input_file,
    model
)


# 輸出 MIDI
with open(output_file, "wb") as f:
    f.write(
        midi_data.get_bytes()
    )


print("MIDI完成:")
print(output_file)