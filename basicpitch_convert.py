import sys
import os

from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH
from basic_pitch.note_creation import model_output_to_notes
from basic_pitch import inference


print("開始 BasicPitch")


if len(sys.argv) < 3:
    print(
        "使用方法: python basicpitch_convert.py input.mp3 output.mid"
    )
    sys.exit(1)



INPUT = os.path.abspath(sys.argv[1])
OUTPUT = os.path.abspath(sys.argv[2])


print("輸入:")
print(INPUT)

print("輸出:")
print(OUTPUT)



# ==========================
# BasicPitch Predict
# ==========================

print("Predicting MIDI for", INPUT)


model_output, midi_data, note_events = predict(
    INPUT,
    ICASSP_2022_MODEL_PATH
)


print("note events:", len(note_events))



# ==========================
# 儲存 MIDI
# ==========================

os.makedirs(
    os.path.dirname(OUTPUT),
    exist_ok=True
)


midi_data.write(
    OUTPUT
)


print("DONE")
print(OUTPUT)