import sys
import os

from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH
from basic_pitch.utilities import note_events_to_midi


input_audio = sys.argv[1]
output_midi = sys.argv[2]


print("BasicPitch input:", input_audio)


model_output, midi_data, note_events = predict(
    input_audio,
    ICASSP_2022_MODEL_PATH
)


with open(output_midi, "wb") as f:
    midi_data.write(f)


print("MIDI完成:", output_midi)