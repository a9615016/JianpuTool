import sys

from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH


if len(sys.argv) < 3:
    print("python basicpitch_convert.py input.wav output.mid")
    exit()


audio = sys.argv[1]
out = sys.argv[2]


print("開始 BasicPitch")
print("輸入:", audio)


model_output, midi_data, note_events = predict(
    audio,
    ICASSP_2022_MODEL_PATH
)


print("note events:", len(note_events))


midi_data.write(out)


print("DONE")
print(out)