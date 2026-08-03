import sys
import os

from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH


def convert_audio_to_midi(
    input_audio,
    output_midi
):

    print("Audio → MIDI")
    print("Input:", input_audio)


    # BasicPitch 推論

    model_output, midi_data, note_events = predict(
        input_audio,
        ICASSP_2022_MODEL_PATH
    )


    # 建立輸出資料夾

    output_dir = os.path.dirname(
        output_midi
    )

    if output_dir:
        os.makedirs(
            output_dir,
            exist_ok=True
        )


    # 寫入 MIDI

    midi_data.write(
        output_midi
    )


    print(
        "MIDI saved:",
        output_midi
    )



if __name__ == "__main__":


    if len(sys.argv) != 3:

        print(
            "使用方式:"
        )

        print(
            "python basicpitch_convert.py input.wav output.mid"
        )

        sys.exit(1)



    input_audio = sys.argv[1]

    output_midi = sys.argv[2]


    convert_audio_to_midi(
        input_audio,
        output_midi
    )