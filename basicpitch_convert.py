import sys
import os

from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH


if len(sys.argv) < 3:
    print(
        "用法: python basicpitch_convert.py input.mp3 output.mid"
    )
    sys.exit(1)


input_audio = sys.argv[1]
output_midi = sys.argv[2]


print("輸入:", input_audio)
print("輸出:", output_midi)


model_output, midi_data, note_events = predict(
    input_audio,
    ICASSP_2022_MODEL_PATH
)


midi_data.write(
    output_midi
)


print("完成 MIDI:", output_midi)