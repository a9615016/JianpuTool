import sys
from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH


def audio_to_midi(input_audio, output_midi):

    print("BasicPitch 開始分析")
    print("輸入:", input_audio)

    model_output, midi_data, note_events = predict(
        input_audio
    )

    midi_data.write(output_midi)

    print("MIDI完成:", output_midi)


if __name__ == "__main__":

    audio = sys.argv[1]
    midi = sys.argv[2]

    audio_to_midi(audio, midi)