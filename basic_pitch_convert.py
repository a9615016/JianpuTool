import sys
import os

from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH


if len(sys.argv) < 3:
    print("usage: python basic_pitch_convert.py input.mp3 output.mid")
    sys.exit(1)


input_audio = sys.argv[1]
output_midi = sys.argv[2]


print("BasicPitch input:")
print(input_audio)


print("Predicting MIDI...")


_, midi_data, _ = predict(
    input_audio,
    model_or_model_path=ICASSP_2022_MODEL_PATH
)


print("Writing MIDI:")

midi_data.write(output_midi)


print("MIDI完成:")
print(output_midi)