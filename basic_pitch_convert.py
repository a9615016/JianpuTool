import sys
import os

print("BASIC PITCH VERSION FIX V3")

from basic_pitch.inference import (
    predict_and_save,
    Model
)

from basic_pitch import ICASSP_2022_MODEL_PATH


if len(sys.argv) < 3:
    print("Usage: python basic_pitch_convert.py input.mp3 output.mid")
    sys.exit(1)


input_audio = sys.argv[1]
output_midi = sys.argv[2]


print("BasicPitch input:")
print(input_audio)


output_dir = os.path.dirname(output_midi)

os.makedirs(output_dir, exist_ok=True)


print("Loading BasicPitch model")

model = Model(ICASSP_2022_MODEL_PATH)


print("Predicting MIDI...")


predict_and_save(
    [input_audio],
    output_dir,
    True,       # save_midi
    False,      # sonify_midi
    False,      # save_model_outputs
    False,      # save_notes
    model
)


print("Searching MIDI...")


found = False


for file in os.listdir(output_dir):

    if file.endswith(".mid"):

        src = os.path.join(output_dir, file)

        if src != output_midi:
            os.rename(src, output_midi)

        found = True
        break


if not found:
    raise Exception("BasicPitch did not generate MIDI")


print("MIDI完成:")
print(output_midi)