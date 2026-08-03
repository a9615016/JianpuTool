import sys
import traceback

try:
    from basic_pitch.inference import predict
    from basic_pitch import ICASSP_2022_MODEL_PATH

    print("BasicPitch import OK")


    input_audio = sys.argv[1]
    output_midi = sys.argv[2]


    print("INPUT:", input_audio)


    model_output, midi_data, note_events = predict(
        input_audio,
        ICASSP_2022_MODEL_PATH
    )


    midi_data.write(
        output_midi
    )


    print("DONE:", output_midi)


except Exception:

    traceback.print_exc()
    sys.exit(1)