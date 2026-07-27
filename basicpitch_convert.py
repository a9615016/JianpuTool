import sys
import os

from pathlib import Path


# BasicPitch

from basic_pitch.inference import (
    predict,
    ICASSP_2022_MODEL_PATH
)

from basic_pitch import (
    audio_to_midi
)



def convert_audio_to_midi(
    input_audio,
    output_midi
):


    print("================")
    print("BasicPitch v26")
    print("Input:")
    print(input_audio)
    print("Output:")
    print(output_midi)
    print("================")



    if not os.path.exists(input_audio):

        raise FileNotFoundError(
            input_audio
        )



    output_dir = os.path.dirname(
        output_midi
    )


    if output_dir:
        os.makedirs(
            output_dir,
            exist_ok=True
        )



    print(
        "開始分析音訊..."
    )



    # ======================
    # BasicPitch 推論
    # ======================


    model_output, midi_data, note_events = predict(
        input_audio,
        ICASSP_2022_MODEL_PATH
    )



    print(
        "音符數:",
        len(note_events)
    )



    # ======================
    # 寫 MIDI
    # ======================


    midi_data.write(
        output_midi
    )


    print(
        "MIDI完成:",
        output_midi
    )




if __name__ == "__main__":


    if len(sys.argv) < 3:

        print(
            "使用:"
        )

        print(
            "python basicpitch_convert.py input.mp3 output.mid"
        )

        sys.exit(1)



    input_file = sys.argv[1]

    output_file = sys.argv[2]



    try:


        convert_audio_to_midi(
            input_file,
            output_file
        )


    except Exception as e:


        print(
            "ERROR:"
        )

        print(e)

        sys.exit(1)