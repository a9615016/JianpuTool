import sys
import os

from basic_pitch.inference import predict_and_save


if len(sys.argv) < 3:
    print("Usage: python basic_pitch_convert.py input.mp3 output.mid")
    exit(1)


input_audio = sys.argv[1]
output_midi = sys.argv[2]


print("BasicPitch input:")
print(input_audio)


output_dir = os.path.dirname(output_midi)

os.makedirs(output_dir, exist_ok=True)


predict_and_save(
    [input_audio],
    output_dir,
    save_midi=True,
    sonify_midi=False,
    save_model_outputs=False,
    save_notes=False
)


# BasicPitch 會自己產生名字
# 找 midi
for f in os.listdir(output_dir):
    if f.endswith(".mid"):
        src = os.path.join(output_dir,f)

        if src != output_midi:
            os.rename(src, output_midi)

        break


print("MIDI完成:")
print(output_midi)