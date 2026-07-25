import sys

from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH
from basic_pitch import note_events_to_midi


if len(sys.argv) < 3:
    print("usage: python basicpitch_convert.py input.mp3 output.mid")
    sys.exit(1)


input_file = sys.argv[1]
output_file = sys.argv[2]


print("================")
print("BasicPitch開始")
print("輸入:", input_file)
print("================")


try:

    result = predict(
        input_file,
        model_or_model_path=ICASSP_2022_MODEL_PATH
    )


    note_events = result[0]


    midi = note_events_to_midi(note_events)


    midi.write(output_file)


    print("================")
    print("MIDI完成")
    print(output_file)
    print("================")


except Exception as e:

    print("BasicPitch錯誤")
    print(e)
    sys.exit(1)