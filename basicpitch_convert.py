from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH
from basic_pitch.note_creation import note_events_to_midi
import sys


input_audio=sys.argv[1]
output_mid=sys.argv[2]


model_path=ICASSP_2022_MODEL_PATH


model_output = predict(
    input_audio,
    model_path
)


note_events = model_output[0]

note_events_to_midi(
    note_events,
    output_mid
)

print("MIDI created:", output_mid)