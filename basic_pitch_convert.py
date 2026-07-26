import sys
import os

from basic_pitch.inference import predict_and_save
from basic_pitch import ICASSP_2022_MODEL_PATH


if len(sys.argv) < 3:
    print("usage: python basic_pitch_convert.py input.mp3 output.mid")
    exit(1)


input_file = sys.argv[1]
output_file = sys.argv[2]

output_dir = os.path.dirname(output_file)


print("BasicPitch input:")
print(input_file)


predict_and_save(
    [input_file],          # audio_paths
    output_dir,            # output_directory
    True,                  # save_midi
    False,                 # sonify_midi
    False,                 # save_model_outputs
    True,                  # save_notes
    ICASSP_2022_MODEL_PATH # model_or_model_path
)


# BasicPitch 預設輸出
generated = os.path.join(
    output_dir,
    os.path.splitext(
        os.path.basename(input_file)
    )[0] + ".mid"
)


if os.path.exists(generated):

    os.rename(
        generated,
        output_file
    )


print("MIDI完成:")
print(output_file)