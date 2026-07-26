import sys

from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH


input_audio = sys.argv[1]
output_midi = sys.argv[2]


print("開始 BasicPitch")
print("輸入:", input_audio)


_, midi_data, note_events = predict(
    input_audio,
    ICASSP_2022_MODEL_PATH
)


midi_data.write(output_midi)


print("MIDI完成")